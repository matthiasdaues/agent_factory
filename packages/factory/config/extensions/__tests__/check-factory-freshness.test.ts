// The freshness check warns once per session when the installed factory copy
// differs from packages/factory in a factory source checkout.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./check-factory-freshness.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import freshnessExtension from "../check-factory-freshness.ts";

type Handler = (event: unknown, ctx: { cwd: string }) => Promise<unknown>;

function loadHandler(): Handler {
  let handler: Handler | undefined;
  freshnessExtension({
    on(name: string, fn: Handler) {
      if (name === "tool_call") handler = fn;
    },
  } as never);
  assert.ok(handler, "extension registers a tool_call handler");
  return handler;
}

function git(cwd: string, ...args: string[]) {
  return execFileSync("git", args, { cwd, encoding: "utf-8" }).trim();
}

type Options = { factory?: boolean; commit?: boolean; manifest?: string | null };

// A git project; the manifest text is written when given.
function project({ factory = true, commit = true, manifest = null }: Options = {}) {
  const root = mkdtempSync(join(tmpdir(), "freshness-"));
  git(root, "init", "--quiet", "-b", "dev");
  if (factory) {
    mkdirSync(join(root, "packages", "factory"), { recursive: true });
    writeFileSync(join(root, "packages", "factory", "f.txt"), "x");
  }
  if (commit) {
    git(root, "add", "-A");
    git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--quiet", "--allow-empty", "-m", "init");
  }
  const hash = () => git(root, "rev-parse", "HEAD:packages/factory");
  if (manifest !== null) {
    mkdirSync(join(root, ".agent-factory"), { recursive: true });
    writeFileSync(join(root, ".agent-factory", "install.json"), manifest);
  }
  return { root, hash, done: () => rmSync(root, { recursive: true, force: true }) };
}

// Runs the handler once and returns what it printed to stderr.
async function warnings(cwd: string, handler = loadHandler()) {
  const seen: string[] = [];
  const original = console.error;
  console.error = (...args: unknown[]) => void seen.push(args.join(" "));
  try {
    await handler({}, { cwd });
  } finally {
    console.error = original;
  }
  return seen;
}

test("freshness: a recorded hash that differs from the tree hash warns", async () => {
  const p = project({ manifest: JSON.stringify({ factory_tree_hash: "stale" }) });
  try {
    const seen = await warnings(p.root);
    assert.equal(seen.length, 1);
    assert.match(seen[0], /out of sync with packages\/factory/);
    assert.match(seen[0], /update-factory --target \./);
  } finally {
    p.done();
  }
});

test("freshness: an empty recorded hash warns", async () => {
  const p = project({ manifest: JSON.stringify({}) });
  try {
    assert.equal((await warnings(p.root)).length, 1);
  } finally {
    p.done();
  }
});

test("freshness: a recorded hash equal to the tree hash stays silent", async () => {
  const p = project({ manifest: "{}" });
  try {
    writeFileSync(join(p.root, ".agent-factory", "install.json"), JSON.stringify({ factory_tree_hash: p.hash() }));
    assert.deepEqual(await warnings(p.root), []);
  } finally {
    p.done();
  }
});

test("freshness: an unreadable manifest stays silent", async () => {
  const p = project({ manifest: "not json" });
  try {
    assert.deepEqual(await warnings(p.root), []);
  } finally {
    p.done();
  }
});

test("freshness: a project without packages/factory stays silent", async () => {
  const p = project({ factory: false, manifest: "{}" });
  try {
    assert.deepEqual(await warnings(p.root), []);
  } finally {
    p.done();
  }
});

test("freshness: a project without an install manifest stays silent", async () => {
  const p = project();
  try {
    assert.deepEqual(await warnings(p.root), []);
  } finally {
    p.done();
  }
});

test("freshness: a project whose HEAD has no factory tree stays silent", async () => {
  const p = project({ commit: false, manifest: "{}" });
  try {
    assert.deepEqual(await warnings(p.root), []);
  } finally {
    p.done();
  }
});

test("freshness: a directory outside git stays silent", async () => {
  const dir = mkdtempSync(join(tmpdir(), "freshness-nogit-"));
  try {
    assert.deepEqual(await warnings(dir), []);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
});

test("freshness: the check runs once per session", async () => {
  const p = project({ manifest: JSON.stringify({ factory_tree_hash: "stale" }) });
  try {
    const handler = loadHandler();
    assert.equal((await warnings(p.root, handler)).length, 1);
    assert.equal((await warnings(p.root, handler)).length, 0);
  } finally {
    p.done();
  }
});
