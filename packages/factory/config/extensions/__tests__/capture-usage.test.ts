// The capture-usage extension hands a human Pi session to the usage capture
// once, at session shutdown. A spy replaces pi-usage.ts, so the tests see the
// exact stream and context the extension passes on.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./capture-usage.test.ts
import { test, beforeEach } from "node:test";
import assert from "node:assert/strict";
import { register } from "node:module";
import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

// envelope-loader.mjs stubs pi-usage.ts for every importer. This later hook
// runs first and serves the spy to modules imported with "?spy" in their URL.
const spySource = `
export const DEPTH_ENV = "SPY_DEPTH_ENV";
export const INLINE_CAPTURE_ENV = "SPY_INLINE_ENV";
export function activeSessionId(manager) {
  const file = manager.getSessionFile();
  return file ? "id-of-" + file.split("/").pop() : "fallback-id";
}
export function canonicalPiModel(cwd, model) {
  return model === undefined ? undefined : "canon:" + model;
}
export function capturePiStream(cwd, stream, context) {
  globalThis.__spyCalls.push({ cwd, stream, context });
}
`;
register(
  "data:text/javascript," +
    encodeURIComponent(`
const spy = ${JSON.stringify(spySource)};
export async function resolve(specifier, context, nextResolve) {
  if (specifier.endsWith("pi-usage.ts") && context.parentURL?.includes("?spy")) {
    return { url: "data:text/javascript," + encodeURIComponent(spy), shortCircuit: true };
  }
  return nextResolve(specifier, context);
}`),
);

type Handler = (event: unknown, ctx: unknown) => Promise<void>;
type Call = { cwd: string; stream: string; context: Record<string, unknown> };
const calls = () => (globalThis as unknown as { __spyCalls: Call[] }).__spyCalls;

// One module instance serves every test, so the coverage report lists the file once.
async function load(): Promise<Handler | undefined> {
  const mod = await import("../capture-usage.ts?spy");
  let handler: Handler | undefined;
  mod.default({
    on(name: string, fn: Handler) {
      if (name === "session_shutdown") handler = fn;
    },
  });
  return handler;
}

const ENV_KEYS = ["SPY_INLINE_ENV", "SPY_DEPTH_ENV", "PI_AGENT_FACTORY_PARENT_SESSION_ID"];
beforeEach(() => {
  (globalThis as unknown as { __spyCalls: Call[] }).__spyCalls = [];
  for (const key of ENV_KEYS) delete process.env[key];
});

const assistant = (model: unknown) => JSON.stringify({ type: "message_end", message: { role: "assistant", model } });

function sessionFile(content: string) {
  const dir = mkdtempSync(join(tmpdir(), "capture-usage-"));
  const file = join(dir, "s-1.jsonl");
  writeFileSync(file, content);
  return { dir, file, done: () => rmSync(dir, { recursive: true, force: true }) };
}

test("capture-usage: inline capture disables the extension", async () => {
  process.env.SPY_INLINE_ENV = "1";
  assert.equal(await load(), undefined);
});

test("capture-usage: the shutdown hands the session file stream to the capture", async () => {
  const s = sessionFile([assistant("a/first"), "not json", "", assistant(5), assistant("z/last")].join("\n"));
  try {
    process.env.PI_AGENT_FACTORY_PARENT_SESSION_ID = "parent-7";
    process.env.SPY_DEPTH_ENV = "3";
    const handler = (await load())!;
    const manager = { getSessionFile: () => s.file, getBranch: () => assert.fail("branch unused") };
    await handler({}, { cwd: "/work", sessionManager: manager });
    assert.equal(calls().length, 1);
    const [call] = calls();
    assert.equal(call.cwd, "/work");
    assert.match(call.stream, /a\/first/);
    assert.deepEqual(call.context, {
      sessionId: "id-of-s-1.jsonl",
      parentSessionId: "parent-7",
      depth: 3,
      agent: "human",
      model: "canon:z/last",
      exitStatus: "success",
    });
  } finally {
    s.done();
  }
});

test("capture-usage: without a session file the branch is rebuilt as events", async () => {
  const handler = (await load())!;
  const branch = [
    { type: "message", message: { role: "assistant", model: "m/x" } },
    { type: "other", value: 1 },
  ];
  await handler({}, { cwd: "/w", sessionManager: { getSessionFile: () => undefined, getBranch: () => branch } });
  const [call] = calls();
  assert.deepEqual(
    call.stream.split("\n").map((line) => JSON.parse(line)),
    [{ type: "message_end", message: { role: "assistant", model: "m/x" } }, { type: "other", value: 1 }],
  );
  assert.equal(call.context.model, "canon:m/x");
  assert.equal(call.context.depth, 0);
  assert.equal(call.context.parentSessionId, undefined);
});

test("capture-usage: a directory or missing path as session file falls back to the branch", async () => {
  const s = sessionFile("");
  try {
    for (const path of [s.dir, join(s.dir, "missing.jsonl")]) {
      const handler = (await load())!;
      await handler({}, { cwd: "/w", sessionManager: { getSessionFile: () => path, getBranch: () => [] } });
    }
    assert.deepEqual(calls().map((c) => c.stream), ["", ""]);
    assert.equal(calls()[0].context.model, undefined);
  } finally {
    s.done();
  }
});

test("capture-usage: a non-numeric depth counts as zero", async () => {
  process.env.SPY_DEPTH_ENV = "deep";
  const handler = (await load())!;
  await handler({}, { cwd: "/w", sessionManager: { getSessionFile: () => undefined, getBranch: () => [] } });
  assert.equal(calls()[0].context.depth, 0);
});

test("capture-usage: only the first shutdown captures", async () => {
  const handler = (await load())!;
  const ctx = { cwd: "/w", sessionManager: { getSessionFile: () => undefined, getBranch: () => [] } };
  await handler({}, ctx);
  await handler({}, ctx);
  assert.equal(calls().length, 1);
});

test("capture-usage: a failing session manager never blocks the shutdown", async () => {
  const handler = (await load())!;
  const broken = {
    getSessionFile: () => undefined,
    getBranch: () => {
      throw new Error("broken");
    },
  };
  await handler({}, { cwd: "/w", sessionManager: broken });
  assert.equal(calls().length, 0);
});
