// Pi's step guard passes each read, write and bash tool call to the project's
// step-guard script and blocks the call when the script exits non-zero.
// A stub script stands in for the real one.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./step-guard.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, existsSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import guardExtension from "../step-guard.ts";

type Handler = (event: unknown, ctx: { cwd: string }) => Promise<unknown>;
type Blocked = { block: boolean; reason: string } | undefined;

function loadHandler(): Handler {
  let handler: Handler | undefined;
  const pi = {
    on(name: string, fn: Handler) {
      if (name === "tool_call") handler = fn;
    },
  };
  guardExtension(pi as never);
  assert.ok(handler, "extension registers a tool_call handler");
  return handler;
}

// A git project whose stub script logs "<args> <stdin>" per call, prints
// `stderr` and exits with `code`; or a project without the script.
function project(code: number | null, stderr = "") {
  const root = mkdtempSync(join(tmpdir(), "step-guard-"));
  execFileSync("git", ["init", "--quiet", root]);
  const scripts = join(root, ".agent-factory", "factory", "scripts");
  mkdirSync(scripts, { recursive: true });
  const log = join(root, "guard.log");
  if (code !== null) {
    const script = join(scripts, "step-guard");
    writeFileSync(
      script,
      `#!/bin/sh\nprintf '%s %s\\n' "$*" "$(cat)" >> '${log}'\n` +
        (stderr ? `echo '${stderr}' >&2\n` : "") +
        `exit ${code}\n`,
    );
    chmodSync(script, 0o755);
  }
  const lines = () => (existsSync(log) ? readFileSync(log, "utf-8").trim().split("\n") : []);
  return { root, lines, done: () => rmSync(root, { recursive: true, force: true }) };
}

async function run(code: number | null, event: unknown, stderr = "") {
  const p = project(code, stderr);
  try {
    const result = (await loadHandler()(event, { cwd: p.root })) as Blocked;
    return { result, lines: p.lines() };
  } finally {
    p.done();
  }
}

for (const toolName of ["unknown", "grep", "glob"]) {
  test(`step-guard: tool '${toolName}' is not guarded and the script never runs`, async () => {
    const { result, lines } = await run(0, { toolName, input: {} });
    assert.equal(result, undefined);
    assert.deepEqual(lines, []);
  });
}

for (const [toolName, type] of [
  ["Read", "read"],
  ["view", "read"],
  ["read_file", "read"],
  ["Edit", "write"],
  ["write", "write"],
  ["write_file", "write"],
  ["create", "write"],
  ["apply_patch", "write"],
  ["bash", "bash"],
] as const) {
  test(`step-guard: tool '${toolName}' is guarded as '${type}'`, async () => {
    const input = type === "bash" ? { command: "ls" } : { path: "a.txt" };
    const { result, lines } = await run(0, { toolName, input });
    assert.equal(result, undefined);
    assert.equal(lines.length, 1);
    assert.ok(lines[0].startsWith(`--guard-type ${type} `), lines[0]);
  });
}

test("step-guard: a write passes filePath, file_path and path as the payload path", async () => {
  for (const key of ["filePath", "file_path", "path"]) {
    const { lines } = await run(0, { toolName: "write", input: { [key]: "x/y.md" } });
    assert.deepEqual(lines, ['--guard-type write {"path":"x/y.md"}']);
  }
});

test("step-guard: a bash call passes command or cmd as the payload command", async () => {
  for (const key of ["command", "cmd"]) {
    const { lines } = await run(0, { toolName: "bash", input: { [key]: "echo hi" } });
    assert.deepEqual(lines, ['--guard-type bash {"command":"echo hi"}']);
  }
});

test("step-guard: a bash call without a command passes an empty command", async () => {
  const { lines } = await run(0, { toolName: "bash", input: undefined });
  assert.deepEqual(lines, ['--guard-type bash {"command":""}']);
});

test("step-guard: a patch passes one payload per touched file", async () => {
  const patch = [
    "*** Begin Patch",
    "*** Add File: a.txt",
    "+x",
    "*** Update File: b/c.txt",
    "*** Delete File: d.txt",
    "*** End Patch",
  ].join("\n");
  const { lines } = await run(0, { toolName: "apply_patch", input: { patch } });
  assert.deepEqual(lines, [
    '--guard-type write {"path":"a.txt"}',
    '--guard-type write {"path":"b/c.txt"}',
    '--guard-type write {"path":"d.txt"}',
  ]);
});

test("step-guard: a patch with no file headers and a call with no path pass an empty path", async () => {
  for (const input of [{ patch: "nothing" }, {}, { path: 5 }]) {
    const { lines } = await run(0, { toolName: "write", input });
    assert.deepEqual(lines, ['--guard-type write {"path":""}']);
  }
});

test("step-guard: a refusing script blocks the call with its stderr", async () => {
  const { result } = await run(2, { toolName: "read", input: { path: "a" } }, "no reading here");
  assert.equal(result?.block, true);
  assert.equal(result.reason, "step-guard read: no reading here");
});

test("step-guard: a refusing script without stderr blocks with the process error", async () => {
  const { result } = await run(1, { toolName: "bash", input: { command: "ls" } });
  assert.equal(result?.block, true);
  assert.match(result.reason, /^step-guard bash: Command failed/);
});

test("step-guard: the first refused patch path stops the later ones", async () => {
  const patch = "*** Add File: a\n*** Add File: b";
  const { result, lines } = await run(2, { toolName: "apply_patch", input: { patch } }, "stop");
  assert.equal(result?.block, true);
  assert.equal(lines.length, 1);
});

test("step-guard: a project without the script blocks the call, as the missing script fails", async () => {
  const { result } = await run(null, { toolName: "bash", input: { command: "ls" } });
  assert.equal(result?.block, true);
});

test("step-guard: a working directory outside any git repository is not guarded", async () => {
  const dir = mkdtempSync(join(tmpdir(), "step-guard-nogit-"));
  try {
    const result = await loadHandler()({ toolName: "bash", input: { command: "ls" } }, { cwd: dir });
    assert.equal(result, undefined);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});
