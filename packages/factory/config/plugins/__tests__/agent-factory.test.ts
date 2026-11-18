// The OpenCode plugin with stub scripts and a stub plugin context in place of
// a real OpenCode session. The context records the hook that setup registers
// through ctx.tool.hook, as OpenCode v2.2.7 does.
//
// FC-18-CT-02: the plugin passes edit, write, patch, shell, and execute calls
// to guard-human-fields in execute.before, blocks on exit 2, and blocks when
// the script is missing.
//
// RL-16-CT-02 (ST-0428): the plugin passes the command of a shell call and the
// JavaScript of an execute call to block-dangerous-git.sh, returns the
// script's answer, and holds no rule of its own.
//
// Run: node --experimental-strip-types --import ./packages/factory/config/extensions/__tests__/envelope-loader.mjs --test packages/factory/config/plugins/__tests__/agent-factory.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { chmodSync, existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import plugin from "../agent-factory.ts";

type Call = { tool: string; input: unknown };
type Hook = (call: Call) => Promise<void>;

async function loadHook(directory: string): Promise<Hook> {
  const hooks: Record<string, Hook> = {};
  await plugin.setup({
    location: { directory },
    tool: { hook: (name: string, hook: Hook) => void (hooks[name] = hook) },
  });
  assert.ok(hooks["execute.before"], "plugin registers execute.before");
  return hooks["execute.before"];
}

// A stub script that logs its stdin and exits with `code`; null leaves it out.
function stub(dir: string, name: string, code: number | null, reason: string) {
  const log = join(dir, "..", "..", "..", "..", `${name}.log`);
  if (code !== null) {
    const script = join(dir, name);
    writeFileSync(script, `#!/bin/sh\ncat >> '${log}'\necho ${reason} >&2\nexit ${code}\n`);
    chmodSync(script, 0o755);
  }
  return log;
}

// A git project with both guard scripts as stubs.
function project({ human = 0, git = 0 }: { human?: number | null; git?: number | null } = {}) {
  const root = mkdtempSync(join(tmpdir(), "agent-factory-plugin-"));
  execFileSync("git", ["init", "--quiet"], { cwd: root });
  const hooks = join(root, ".agent-factory", "factory", "config", "hooks");
  mkdirSync(hooks, { recursive: true });
  return {
    root,
    log: stub(hooks, "guard-human-fields", human, "refused"),
    gitLog: stub(hooks, "block-dangerous-git.sh", git, "stub-git-refused"),
    done: () => rmSync(root, { recursive: true, force: true }),
  };
}

const GUARDED = [
  ["edit", { filePath: "docs/findings/BUG-0037.md", oldString: "a", newString: "b" }],
  ["write", { filePath: "docs/findings/BUG-0037.md", content: "x" }],
  ["patch", { patchText: "*** Begin Patch\n*** End Patch" }],
  ["shell", { command: "sed -i s/a/b/ docs/findings/BUG-0037.md" }],
  ["execute", { code: "await Bun.write('docs/findings/BUG-0037.md', 'x')" }],
] as const;

for (const [tool, input] of GUARDED) {
  test(`FC-18-CT-02: ${tool} call runs when the guard exits 0`, async () => {
    const p = project();
    try {
      await (await loadHook(p.root))({ tool, input });
      assert.deepEqual(JSON.parse(readFileSync(p.log, "utf-8")), {
        cwd: p.root,
        toolName: tool,
        input,
      });
    } finally {
      p.done();
    }
  });

  test(`FC-18-CT-02: ${tool} call is blocked when the guard exits 2`, async () => {
    const p = project({ human: 2 });
    try {
      await assert.rejects((await loadHook(p.root))({ tool, input }), /guard-human-fields: refused/);
    } finally {
      p.done();
    }
  });

  test(`FC-18-CT-02: ${tool} call is blocked when the guard script is missing`, async () => {
    const p = project({ human: null });
    try {
      await assert.rejects(
        (await loadHook(p.root))({ tool, input }),
        /guard script missing at .*guard-human-fields/,
      );
    } finally {
      p.done();
    }
  });
}

test("FC-18-CT-02: a tool outside the list never reaches the guard", async () => {
  const p = project({ human: 2, git: 2 });
  try {
    await (await loadHook(p.root))({ tool: "read", input: { filePath: "README.md" } });
  } finally {
    p.done();
  }
});

// RL-16-CT-02 and its execute test: the command text each tool hands the script.
const GIT_GUARDED = [
  ["shell", { command: "dispatch return-story ST-0350" }, "dispatch return-story ST-0350"],
  ["execute", { code: 'execSync("dispatch return-story ST-0350")' }, 'execSync("dispatch return-story ST-0350")'],
] as const;

for (const [tool, input, command] of GIT_GUARDED) {
  test(`RL-16-CT-02: the ${tool} call is blocked with the reason of block-dangerous-git.sh`, async () => {
    const p = project({ git: 2 });
    try {
      await assert.rejects((await loadHook(p.root))({ tool, input }), /^Error: stub-git-refused$/);
      assert.deepEqual(JSON.parse(readFileSync(p.gitLog, "utf-8")), { toolName: tool, input: { command } });
    } finally {
      p.done();
    }
  });

  test(`RL-16-CT-02: the ${tool} call runs dispatch return-story when block-dangerous-git.sh allows it`, async () => {
    const p = project({ git: 0 });
    try {
      await (await loadHook(p.root))({ tool, input });
      assert.deepEqual(JSON.parse(readFileSync(p.gitLog, "utf-8")), { toolName: tool, input: { command } });
    } finally {
      p.done();
    }
  });

  test(`RL-16-CT-02: the ${tool} call is blocked when block-dangerous-git.sh is missing`, async () => {
    const p = project({ git: null });
    try {
      await assert.rejects(
        (await loadHook(p.root))({ tool, input }),
        /block-dangerous-git: guard script missing at .*block-dangerous-git\.sh/,
      );
    } finally {
      p.done();
    }
  });
}

test("RL-16-CT-02: a linked worktree finds block-dangerous-git.sh in the primary checkout", async () => {
  const p = project({ git: 2 });
  try {
    execFileSync("git", ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "--allow-empty", "-m", "init"], { cwd: p.root });
    const worktree = join(p.root, "wt");
    execFileSync("git", ["worktree", "add", "--quiet", worktree], { cwd: p.root });
    await assert.rejects(
      (await loadHook(worktree))({ tool: "shell", input: { command: "dispatch return-story ST-0350" } }),
      /stub-git-refused/,
    );
  } finally {
    p.done();
  }
});

for (const [tool, input] of GUARDED.filter(([tool]) => tool === "edit" || tool === "write" || tool === "patch")) {
  test(`RL-16-CT-02: the ${tool} call never reaches block-dangerous-git.sh`, async () => {
    const p = project({ git: 2 });
    try {
      await (await loadHook(p.root))({ tool, input });
      assert.equal(existsSync(p.gitLog), false);
    } finally {
      p.done();
    }
  });
}
