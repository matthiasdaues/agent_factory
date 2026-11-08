// FC-18-CT-01: the Pi guard extension passes edit, write, patch, and shell
// calls to the guard script, blocks on exit 2, and blocks when the script is
// missing. A stubbed Pi API replaces the real one.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./guard-human-fields.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import guardExtension from "../guard-human-fields.ts";

type Handler = (event: unknown, ctx: { cwd: string }) => Promise<unknown>;

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

// A git project whose guard script exits with `code` and logs its stdin.
function project(code: number | null) {
  const root = mkdtempSync(join(tmpdir(), "guard-human-fields-"));
  execFileSync("git", ["init", "--quiet"], { cwd: root });
  const hooks = join(root, ".agent-factory", "factory", "config", "hooks");
  mkdirSync(hooks, { recursive: true });
  const log = join(root, "guard-input.log");
  if (code !== null) {
    const script = join(hooks, "guard-human-fields");
    writeFileSync(
      script,
      `#!/bin/sh\ncat >> '${log}'\necho refused >&2\nexit ${code}\n`,
    );
    chmodSync(script, 0o755);
  }
  return { root, log, done: () => rmSync(root, { recursive: true, force: true }) };
}

const GUARDED = [
  ["edit", { path: "docs/findings/FAGAN-0042.md" }],
  ["write", { path: "docs/findings/FAGAN-0042.md", content: "x" }],
  ["write_file", { path: "docs/findings/FAGAN-0042.md", content: "x" }],
  ["create", { path: "docs/findings/FAGAN-0042.md", content: "x" }],
  ["apply_patch", { patch: "*** Begin Patch\n*** End Patch" }],
  ["bash", { command: "sed -i s/a/b/ docs/findings/FAGAN-0042.md" }],
] as const;

for (const [toolName, input] of GUARDED) {
  test(`FC-18-CT-01: ${toolName} call runs when the guard exits 0`, async () => {
    const p = project(0);
    try {
      const result = await loadHandler()({ toolName, input }, { cwd: p.root });
      assert.equal(result, undefined);
      assert.deepEqual(JSON.parse(readFileSync(p.log, "utf-8")), { toolName, input });
    } finally {
      p.done();
    }
  });

  test(`FC-18-CT-01: ${toolName} call is blocked when the guard exits 2`, async () => {
    const p = project(2);
    try {
      const result = (await loadHandler()({ toolName, input }, { cwd: p.root })) as {
        block: boolean;
        reason: string;
      };
      assert.equal(result.block, true);
      assert.match(result.reason, /refused/);
    } finally {
      p.done();
    }
  });

  test(`FC-18-CT-01: ${toolName} call is blocked when the guard script is missing`, async () => {
    const p = project(null);
    try {
      const result = (await loadHandler()({ toolName, input }, { cwd: p.root })) as {
        block: boolean;
        reason: string;
      };
      assert.equal(result.block, true);
      assert.match(result.reason, /guard-human-fields/);
      assert.match(result.reason, /missing/);
    } finally {
      p.done();
    }
  });
}

test("FC-18-CT-01: a read call never reaches the guard", async () => {
  const p = project(2);
  try {
    const result = await loadHandler()(
      { toolName: "read", input: { path: "docs/findings/FAGAN-0042.md" } },
      { cwd: p.root },
    );
    assert.equal(result, undefined);
    assert.throws(() => readFileSync(p.log));
  } finally {
    p.done();
  }
});

test("FC-18-CT-01: a read call passes even when the guard script is missing", async () => {
  const p = project(null);
  try {
    const result = await loadHandler()({ toolName: "read", input: {} }, { cwd: p.root });
    assert.equal(result, undefined);
  } finally {
    p.done();
  }
});
