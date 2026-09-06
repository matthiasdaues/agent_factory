// Regression test for BUG-0011 — dispatch_wave spawn-abort misreporting.
//
// Verifies that spawnPi does NOT pass the parent agent-turn AbortSignal into
// node:child_process spawn() options, and that a pre-aborted signal produces a
// distinct cancellation outcome instead of the misleading
// "failed to spawn pi: The operation was aborted".
//
// Uses an injectable spawnFn to deterministically drive the abort path without
// launching a real pi subprocess.
//
// Run: node --experimental-strip-types --import ./envelope-loader.mjs --test ./spawn-abort.test.ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { EventEmitter } from "node:events";
import { spawn, type ChildProcess } from "node:child_process";
import { spawnPi, type SpawnResult } from "../dispatch-wave.ts";

const CANCELLATION_GRACE_MS = 250; // mirrors dispatch-wave.ts

// ── Mock child process that mirrors just enough of ChildProcess to exercise
//    the spawnPi control flow. ──────────────────────────────────────────────

let capturedOptions: Record<string, unknown> | undefined;

class MockChild extends EventEmitter {
  stdout = new EventEmitter();
  stderr = new EventEmitter();
  pid = 99_001;

  kill(sig: string): boolean {
    this.emit("close", null, sig);
    return true;
  }

  unref() {
    // no-op for mock — just needs to exist
  }
}

function mockSpawn(
  cmd: string,
  args: string[],
  opts?: Record<string, unknown>,
): MockChild {
  capturedOptions = opts;
  const child = new MockChild();
  // Simulate real Node.js: if signal is in spawn options and already aborted,
  // the child receives an AbortError ("The operation was aborted").
  if (opts?.signal && (opts.signal as AbortSignal).aborted) {
    process.nextTick(() => {
      child.emit("error", new Error("The operation was aborted"));
    });
  }
  return child as unknown as MockChild;
}

// ── Tests ──────────────────────────────────────────────────────────────────

test("pre-aborted signal: spawn NOT called with signal; reports cancellation", async () => {
  const controller = new AbortController();
  controller.abort();

  capturedOptions = undefined;
  const result: SpawnResult = await spawnPi(
    ["--version"],
    "/tmp",
    1,
    controller.signal,
    "test-session",
    undefined,
    undefined,
    mockSpawn,
  );

  // Signal must NOT be passed to spawn options (BUG-0011 fix).
  assert.equal(
    capturedOptions?.signal,
    undefined,
    "signal must not be in spawn options",
  );
  // Cancellation must be reported distinctly.
  assert.equal(result.cancelled, true, "should report cancelled=true");
  // Must NOT surface the misleading "The operation was aborted" as a spawn error.
  assert.equal(result.error, null, "cancelled spawn must not report an error");
});

test("genuine ENOENT still surfaces as real error (not cancellation)", async () => {
  const controller = new AbortController(); // NOT aborted

  capturedOptions = undefined;
  const enoentSpawn = (
    _cmd: string,
    _args: string[],
    opts?: Record<string, unknown>,
  ): MockChild => {
    capturedOptions = opts;
    const child = new MockChild();
    // Simulate a genuine ENOENT spawn failure (unrelated to the signal).
    process.nextTick(() => {
      child.emit("error", new Error("spawn pi ENOENT"));
    });
    return child as unknown as MockChild;
  };

  const result: SpawnResult = await spawnPi(
    ["--version"],
    "/tmp",
    1,
    controller.signal,
    "test-session",
    undefined,
    undefined,
    enoentSpawn,
  );

  assert.ok(result.error?.includes("ENOENT"), "should report ENOENT error");
  assert.equal(result.cancelled, false, "ENOENT is not a cancellation");
});

test("no abort: normal successful spawn reports ok", async () => {
  const controller = new AbortController(); // not aborted

  capturedOptions = undefined;
  const okSpawn = (
    _cmd: string,
    _args: string[],
    opts?: Record<string, unknown>,
  ): MockChild => {
    capturedOptions = opts;
    const child = new MockChild();
    process.nextTick(() => {
      child.emit("close", 0);
    });
    return child as unknown as MockChild;
  };

  const result: SpawnResult = await spawnPi(
    ["--version"],
    "/tmp",
    1,
    controller.signal,
    "test-session",
    undefined,
    undefined,
    okSpawn,
  );

  assert.equal(result.cancelled, false, "should not be cancelled");
  assert.equal(result.error, null, "should have no error");
  assert.equal(result.status, 0, "should have exit code 0");
});

test("mid-run abort terminates a real child process within grace window", { timeout: 5000 }, async () => {
  const controller = new AbortController();

  // A long-running real child that we can actually kill.
  const realChild = spawn("sleep", ["30"], {
    cwd: "/tmp",
    env: process.env,
    stdio: ["ignore", "pipe", "pipe"],
    detached: process.platform !== "win32",
  });
  if (process.platform !== "win32") {
    realChild.unref();
  }
  realChild.stdout?.resume();
  realChild.stderr?.resume();

  // Inject a spawnFn that returns our pre-spawned real child.
  const injectSpawn = (
    _cmd: string,
    _args: string[],
    _opts?: Record<string, unknown>,
  ): ChildProcess => {
    return realChild;
  };

  // Give the child a moment to start, then abort.
  await new Promise<void>((resolve) => setTimeout(resolve, 100));
  assert.equal(realChild.exitCode, null, "child must be running before abort");

  const [result] = await Promise.all([
    spawnPi(
      ["--version"],
      "/tmp",
      1,
      controller.signal,
      "test-session",
      undefined,
      undefined,
      injectSpawn,
    ),
    (async () => {
      // Trigger abort after a tiny delay to exercise the mid-run path.
      await new Promise((r) => setTimeout(r, 50));
      controller.abort();
    })(),
  ]);

  // Result must report distinct cancellation.
  assert.equal(result.cancelled, true, "mid-run abort must report cancelled");
  assert.equal(result.error, null, "cancellation must not surface as spawn error");

  // The real child must have exited (non-zero) within the grace window + drain.
  // Give it the grace + drain + small cushion to be safe.
  const exitCode = await new Promise<number | null>((resolve) => {
    if (realChild.exitCode !== null) {
      resolve(realChild.exitCode);
      return;
    }
    const timer = setTimeout(() => resolve(realChild.exitCode ?? -1), CANCELLATION_GRACE_MS + 800 + 500);
    realChild.once("close", (code: number | null) => {
      clearTimeout(timer);
      resolve(code);
    });
  });

  assert.notEqual(exitCode, null, "real child must have exited after abort");
  assert.ok(exitCode !== 0, "child must exit non-zero (killed by signal)");
});
