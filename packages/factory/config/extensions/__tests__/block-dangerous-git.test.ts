// BUG-0124: the Pi merge gate denies git merge while the stop holds, even when
// a premerge-check-ok marker from before the stop exists. A stop check that
// cannot run denies the merge. A stubbed Pi API replaces the real one.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./block-dangerous-git.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import gateExtension from "../block-dangerous-git.ts";

type Handler = (event: unknown, ctx: { cwd: string }) => Promise<unknown>;

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

// A git project with branch feat/x and a premerge-check-ok marker for its head.
// `stub` is the text of the stop check (dispatch_lib.py), or null for none.
function project(stub: string | null) {
  const root = mkdtempSync(join(tmpdir(), "block-dangerous-git-"));
  git(root, "init", "--quiet", "-b", "dev");
  git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "--allow-empty", "-m", "init");
  git(root, "branch", "feat/x");
  const head = git(root, "rev-parse", "feat/x");
  mkdirSync(join(root, ".current-work"));
  writeFileSync(join(root, ".current-work", "premerge-check-ok"), `branch=feat/x\nhead=${head}\n`);
  if (stub !== null) {
    const scripts = join(root, ".agent-factory", "factory", "scripts");
    mkdirSync(scripts, { recursive: true });
    writeFileSync(join(scripts, "dispatch_lib.py"), stub);
  }
  return { root, done: () => rmSync(root, { recursive: true, force: true }) };
}

const merge = { toolName: "bash", input: { command: "git merge feat/x" } };

type Blocked = { block: boolean; reason: string } | undefined;

test("BUG-0124: a merge with a valid earlier marker is blocked while the stop holds", async () => {
  const p = project('def stop_notice(cwd=None):\n    return "STOP: BUG-0037 stops the run"\n');
  try {
    const result = (await loadHandler()(merge, { cwd: p.root })) as Blocked;
    assert.equal(result?.block, true);
    assert.match(result.reason, /BUG-0037/);
  } finally {
    p.done();
  }
});

test("BUG-0124: a merge with a valid marker runs when no stop holds", async () => {
  const p = project("def stop_notice(cwd=None):\n    return None\n");
  try {
    assert.equal(await loadHandler()(merge, { cwd: p.root }), undefined);
  } finally {
    p.done();
  }
});

test("BUG-0124: a merge is blocked when the stop check is missing", async () => {
  const p = project(null);
  try {
    const result = (await loadHandler()(merge, { cwd: p.root })) as Blocked;
    assert.equal(result?.block, true);
    assert.match(result.reason, /stop check/);
  } finally {
    p.done();
  }
});
