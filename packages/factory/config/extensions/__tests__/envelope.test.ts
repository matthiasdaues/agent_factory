// Test harness for the pure envelope-parser functions in run-agent.ts.
// Stubs the extension's external imports (pi API, typebox, pi-usage) so the
// parser can be exercised without spawning a pi subprocess.
import { test } from "node:test";
import assert from "node:assert/strict";
import { execSync } from "node:child_process";
import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  childCommitsSince,
  enrichWithChildCommits,
  extractEnvelopeObject,
  gitLocalHead,
  parseChildResultEnvelope,
} from "../run-agent.ts";

const good = {
  disposition: "pass",
  finding_counts: { critical: 0, major: 0, minor: 0 },
  artifact_paths: ["docs/reviews/x.md"],
  next_action: "Proceed to the next phase.",
};

const goodText = JSON.stringify(good);

test("parses a bare JSON envelope", () => {
  const r = parseChildResultEnvelope(goodText);
  assert.equal(r.error, undefined);
  assert.equal(r.envelope?.disposition, "pass");
});

test("recovers the envelope wrapped in a Markdown fence", () => {
  const r = parseChildResultEnvelope("```json\n" + goodText + "\n```");
  assert.equal(r.error, undefined);
  assert.equal(r.envelope?.next_action, good.next_action);
});

test("recovers the envelope with trailing prose", () => {
  const r = parseChildResultEnvelope(goodText + "\nDone. Everything passed.");
  assert.equal(r.error, undefined);
});

test("recovers the envelope with leading prose", () => {
  const r = parseChildResultEnvelope("Here you go:\n" + goodText);
  assert.equal(r.error, undefined);
});

test("recovers a fence with a language tag and surrounding text", () => {
  const r = parseChildResultEnvelope(
    "Result:\n```javascript\nconst e = " + goodText + ";\n```\nall set",
  );
  assert.equal(r.error, undefined);
  assert.equal(r.envelope?.disposition, "pass");
});

test("rejects a structurally valid object missing canonical fields", () => {
  const r = parseChildResultEnvelope(JSON.stringify({ foo: 1 }));
  assert.ok(r.error && r.error.includes("four canonical fields"));
});

test("rejects non-JSON text", () => {
  const r = parseChildResultEnvelope("the child produced no structured result");
  assert.ok(r.error && r.error.includes("expected one exact JSON object"));
});

test("extractEnvelopeObject returns undefined for empty text", () => {
  assert.equal(extractEnvelopeObject("   "), undefined);
});

test("finds the last balanced object among prose", () => {
  const text = "prefix text " + JSON.stringify({ a: 1 }) + " more prose " + goodText;
  const v = extractEnvelopeObject(text);
  assert.deepEqual(v, good);
});

function makeRepo(): string {
  const dir = mkdtempSync(join(tmpdir(), "envtest-"));
  execSync("git init -q", { cwd: dir });
  execSync("git config user.email test@example.com", { cwd: dir });
  execSync("git config user.name test", { cwd: dir });
  return dir;
}

function commit(dir: string, file: string, msg: string): void {
  writeFileSync(join(dir, file), msg, "utf-8");
  execSync(`git add ${file}`, { cwd: dir });
  execSync(`git commit -q -m "${msg}"`, { cwd: dir });
}

test("gitLocalHead returns the current HEAD", () => {
  const dir = makeRepo();
  commit(dir, "a.txt", "first");
  const head = gitLocalHead(dir);
  assert.ok(head && /^[0-9a-f]{12}$/.test(head));
  execSync("rm -rf " + dir);
});

test("gitLocalHead returns null outside a git repo", () => {
  assert.equal(gitLocalHead(tmpdir()), null);
});

test("childCommitsSince lists commits above the base", () => {
  const dir = makeRepo();
  commit(dir, "a.txt", "base");
  const base = gitLocalHead(dir) as string;
  commit(dir, "b.txt", "child-one");
  commit(dir, "c.txt", "child-two");
  const commits = childCommitsSince(dir, base);
  assert.ok(commits && commits.length === 2);
  assert.match(commits[0], /child-two/);
  assert.match(commits[1], /child-one/);
  execSync("rm -rf " + dir);
});

test("childCommitsSince returns null when no new commits", () => {
  const dir = makeRepo();
  commit(dir, "a.txt", "base");
  const base = gitLocalHead(dir) as string;
  assert.equal(childCommitsSince(dir, base), null);
  execSync("rm -rf " + dir);
});

// --- FAGAN-0016: commit disclosure on all error paths ---

test("enrichWithChildCommits adds commit disclosure when commits exist (FAGAN-0016)", () => {
  const dir = makeRepo();
  commit(dir, "a.txt", "base");
  const base = gitLocalHead(dir) as string;
  commit(dir, "b.txt", "child-work");
  const result = enrichWithChildCommits(dir, base, { agent: "test", error: true });
  assert.ok(Array.isArray((result as any).freshChildCommits));
  assert.equal((result as any).freshChildCommits.length, 1);
  assert.ok((result as any).note.includes("do not blindly re-dispatch"));
  assert.equal((result as any).agent, "test");
  execSync("rm -rf " + dir);
});

test("enrichWithChildCommits returns base when no new commits (FAGAN-0016)", () => {
  const dir = makeRepo();
  commit(dir, "a.txt", "base");
  const base = gitLocalHead(dir) as string;
  const result = enrichWithChildCommits(dir, base, { agent: "test", error: true });
  assert.deepEqual(result, { agent: "test", error: true });
  execSync("rm -rf " + dir);
});

test("enrichWithChildCommits returns base when headBefore is null (FAGAN-0016)", () => {
  const result = enrichWithChildCommits(tmpdir(), null, { agent: "test" });
  assert.deepEqual(result, { agent: "test" });
});

// --- FAGAN-0017: envelope preference over larger sibling ---

test("extractEnvelopeObject prefers envelope over larger sibling (FAGAN-0017)", () => {
  const larger = JSON.stringify({ a: { b: 1, c: 2, d: 3, e: 4, f: 5 } });
  const text = goodText + " example: " + larger;
  const v = extractEnvelopeObject(text);
  assert.deepEqual(v, good);
});

test("extractEnvelopeObject finds envelope when it is the rightmost (FAGAN-0017)", () => {
  const smaller = JSON.stringify({ a: 1 });
  const text = smaller + " " + goodText;
  const v = extractEnvelopeObject(text);
  assert.deepEqual(v, good);
});

test("extractEnvelopeObject falls back to largest when no envelope-shaped (FAGAN-0017)", () => {
  const small = JSON.stringify({ x: 1 });
  const big = JSON.stringify({ x: 1, y: 2, z: 3, w: 4 });
  const text = small + " " + big;
  const v = extractEnvelopeObject(text);
  assert.deepEqual(v, { x: 1, y: 2, z: 3, w: 4 });
});
