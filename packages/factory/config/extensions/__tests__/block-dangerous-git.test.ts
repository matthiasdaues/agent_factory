// RL-16-CT-01: pi's git guardrail passes each bash command to the script
// block-dangerous-git.sh and returns its answer. It holds no rule of its own:
// with a stub script that allows all, it allows every command. A stubbed pi
// API replaces the real one. The rules themselves are tested against the
// script in tests/factory/test_block_dangerous_git.py and test_finding_stop.py.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./block-dangerous-git.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import gateExtension from "../block-dangerous-git.ts";

type Handler = (event: unknown, ctx: { cwd: string }) => Promise<unknown>;
type Blocked = { block: boolean; reason: string } | undefined;

function loadHandler(): Handler {
  let handler: Handler | undefined;
  const pi = {
    on(name: string, fn: Handler) {
      if (name === "tool_call") handler = fn;
    },
  };
  gateExtension(pi as never);
  assert.ok(handler, "extension registers a tool_call handler");
  return handler;
}

function git(cwd: string, ...args: string[]) {
  return execFileSync("git", args, { cwd, encoding: "utf-8" }).trim();
}

// A git project whose stub script exits with `code` and logs its stdin, or a
// project without the script when `code` is null.
function project(code: number | null) {
  const root = mkdtempSync(join(tmpdir(), "block-dangerous-git-"));
  git(root, "init", "--quiet", "-b", "dev");
  git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "--allow-empty", "-m", "init");
  const hooks = join(root, ".agent-factory", "factory", "config", "hooks");
  mkdirSync(hooks, { recursive: true });
  const log = join(root, "guard-input.log");
  if (code !== null) {
    writeFileSync(
      join(hooks, "block-dangerous-git.sh"),
      `cat >> '${log}'\necho "stub answer ${code}" >&2\nexit ${code}\n`,
    );
  }
  return { root, log, done: () => rmSync(root, { recursive: true, force: true }) };
}

const PUSH = ["git", "push", "origin", "dev"].join(" ");
const COMMANDS = [PUSH, "dispatch close --drop", "dispatch return-story ST-0350", "git status"];

for (const command of COMMANDS) {
  const event = { toolName: "bash", input: { command } };

  test(`RL-16-CT-01: '${command}' runs when the stub script allows it`, async () => {
    const p = project(0);
    try {
      assert.equal(await loadHandler()(event, { cwd: p.root }), undefined);
      assert.deepEqual(JSON.parse(readFileSync(p.log, "utf-8")), event);
    } finally {
      p.done();
    }
  });

  test(`RL-16-CT-01: '${command}' is blocked with the stub's answer when the stub refuses it`, async () => {
    const p = project(2);
    try {
      const result = (await loadHandler()(event, { cwd: p.root })) as Blocked;
      assert.equal(result?.block, true);
      assert.equal(result.reason, "stub answer 2");
    } finally {
      p.done();
    }
  });
}

test("RL-16-CT-01: a bash call is blocked when the script is missing", async () => {
  const p = project(null);
  try {
    const result = (await loadHandler()(
      { toolName: "bash", input: { command: "git status" } },
      { cwd: p.root },
    )) as Blocked;
    assert.equal(result?.block, true);
    assert.match(result.reason, /block-dangerous-git/);
    assert.match(result.reason, /missing/);
  } finally {
    p.done();
  }
});

test("RL-16-CT-01: a linked worktree finds the script of the primary checkout", async () => {
  const p = project(2);
  const wt = join(p.root, ".current-work", "story", "ST-0350");
  try {
    git(p.root, "worktree", "add", "--quiet", "-b", "story/ST-0350", wt, "HEAD");
    const result = (await loadHandler()(
      { toolName: "bash", input: { command: "git status" } },
      { cwd: wt },
    )) as Blocked;
    assert.equal(result?.reason, "stub answer 2");
  } finally {
    p.done();
  }
});

test("RL-16-CT-01: a call of another tool never reaches the script", async () => {
  const p = project(2);
  try {
    const result = await loadHandler()(
      { toolName: "read", input: { path: "README.md" } },
      { cwd: p.root },
    );
    assert.equal(result, undefined);
    assert.throws(() => readFileSync(p.log));
  } finally {
    p.done();
  }
});
