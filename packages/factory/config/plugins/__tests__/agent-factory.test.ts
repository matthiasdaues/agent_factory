// FC-18-CT-02: the guard-only OpenCode plugin passes edit, write, patch,
// shell, and execute calls to the guard script in execute.before, blocks on
// exit 2, and blocks when the script is missing. A stubbed OpenCode API
// replaces the real one.
//
// Run: node --experimental-strip-types --import ./packages/factory/config/extensions/__tests__/envelope-loader.mjs --test packages/factory/config/plugins/__tests__/agent-factory.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import plugin from "../agent-factory.ts";

type Hook = (call: { tool: string; args: unknown }) => Promise<void>;

async function loadHook(directory: string): Promise<Hook> {
  const hooks = (await plugin.setup({ directory } as never)) as Record<string, Hook>;
  assert.ok(hooks["execute.before"], "plugin registers execute.before");
  return hooks["execute.before"];
}

// A git project whose guard script exits with `code` and logs its stdin.
function project(code: number | null) {
  const root = mkdtempSync(join(tmpdir(), "agent-factory-plugin-"));
  execFileSync("git", ["init", "--quiet"], { cwd: root });
  const hooks = join(root, ".agent-factory", "factory", "config", "hooks");
  mkdirSync(hooks, { recursive: true });
  const log = join(root, "guard-input.log");
  if (code !== null) {
    const script = join(hooks, "guard-human-fields");
    writeFileSync(script, `#!/bin/sh\ncat >> '${log}'\necho refused >&2\nexit ${code}\n`);
    chmodSync(script, 0o755);
  }
  return { root, log, done: () => rmSync(root, { recursive: true, force: true }) };
}

const GUARDED = [
  ["edit", { filePath: "docs/findings/BUG-0037.md", oldString: "a", newString: "b" }],
  ["write", { filePath: "docs/findings/BUG-0037.md", content: "x" }],
  ["patch", { patchText: "*** Begin Patch\n*** End Patch" }],
  ["shell", { command: "sed -i s/a/b/ docs/findings/BUG-0037.md" }],
  ["execute", { code: "await Bun.write('docs/findings/BUG-0037.md', 'x')" }],
] as const;

for (const [tool, args] of GUARDED) {
  test(`FC-18-CT-02: ${tool} call runs when the guard exits 0`, async () => {
    const p = project(0);
    try {
      await (await loadHook(p.root))({ tool, args });
      assert.deepEqual(JSON.parse(readFileSync(p.log, "utf-8")), {
        cwd: p.root,
        toolName: tool,
        input: args,
      });
    } finally {
      p.done();
    }
  });

  test(`FC-18-CT-02: ${tool} call is blocked when the guard exits 2`, async () => {
    const p = project(2);
    try {
      await assert.rejects((await loadHook(p.root))({ tool, args }), /refused/);
    } finally {
      p.done();
    }
  });

  test(`FC-18-CT-02: ${tool} call is blocked when the guard script is missing`, async () => {
    const p = project(null);
    try {
      await assert.rejects(
        (await loadHook(p.root))({ tool, args }),
        /guard script missing at .*guard-human-fields/,
      );
    } finally {
      p.done();
    }
  });
}

test("FC-18-CT-02: a tool outside the list never reaches the guard", async () => {
  const p = project(2);
  try {
    await (await loadHook(p.root))({ tool: "read", args: { filePath: "README.md" } });
  } finally {
    p.done();
  }
});
