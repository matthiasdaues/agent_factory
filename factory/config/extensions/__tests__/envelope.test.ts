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
