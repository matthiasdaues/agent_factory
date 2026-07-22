#!/usr/bin/env node
/** Detached Pi capture supervisor: one owner for terminal cleanup. */
import { spawn } from "node:child_process";
import { randomUUID } from "node:crypto";
import {
  chmodSync,
  closeSync,
  constants,
  existsSync,
  lstatSync,
  mkdirSync,
  openSync,
  readFileSync,
  realpathSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { basename, dirname, isAbsolute, join, normalize, resolve } from "node:path";

const FILE_MODE = 0o600;
const DIR_MODE = 0o700;

function fail(message) {
  throw new Error(message);
}

function regularNoLink(path) {
  const info = lstatSync(path);
  return info.isFile() && !info.isSymbolicLink();
}

function parseArgs(argv) {
  const split = argv.indexOf("--capture-command");
  if (split < 0) fail("missing capture command");
  const values = {};
  for (let index = 0; index < split; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith("--") || value === undefined) fail("invalid supervisor arguments");
    values[key.slice(2)] = value;
  }
  return { values, command: argv.slice(split + 1) };
}

function validate(values) {
  const root = realpathSync(values.root);
  if (!isAbsolute(values.root) || normalize(resolve(values.root)) !== values.root || root !== values.root) {
    fail("invalid root");
  }
  const control = join(root, ".agent-factory", "usage-control");
  const pending = join(control, "pending");
  const scratch = join(root, ".agent-factory", "usage", ".capture");
  if (realpathSync(control) !== control || realpathSync(pending) !== pending || realpathSync(scratch) !== scratch) {
    fail("redirected lifecycle directory");
  }
  const marker = values.marker;
  const source = values.source;
  const status = values.status;
  if (
    !isAbsolute(marker) ||
    dirname(marker) !== pending ||
    !basename(marker).endsWith(".pending.json") ||
    !regularNoLink(marker)
  ) {
    fail("invalid marker");
  }
  if (!isAbsolute(source) || dirname(source) !== scratch || !regularNoLink(source)) {
    fail("invalid source");
  }
  const expectedStatus = join(control, basename(marker).replace(/\.pending\.json$/, ".completion.json"));
  if (!isAbsolute(status) || status !== expectedStatus || existsSync(status)) {
    fail("invalid status");
  }
  const registration = JSON.parse(readFileSync(marker, "utf-8"));
  if (registration.generation !== values.generation || registration.staged_source !== source) {
    fail("registration mismatch");
  }
  const committing = marker.replace(/\.pending\.json$/, ".committing.json");
  return { root, control, pending, scratch, marker, committing, source, status, generation: values.generation };
}

function unlinkValidated(path, parent, suffix) {
  try {
    if (dirname(path) !== parent || !basename(path).endsWith(suffix) || !regularNoLink(path)) return;
    unlinkSync(path);
  } catch {}
}

function lifecycleAllowsDiagnostic(ctx) {
  try {
    if (realpathSync(ctx.control) !== ctx.control) return false;
    const state = JSON.parse(readFileSync(join(ctx.control, "state.json"), "utf-8"));
    return state.generation === ctx.generation && ["active", "drain"].includes(state.mode);
  } catch {
    return false;
  }
}

function diagnostic(ctx, reason, exitCode, signal) {
  if (!lifecycleAllowsDiagnostic(ctx)) return;
  try {
    const directory = join(ctx.control, "diagnostics");
    if (!existsSync(directory)) {
      try {
        mkdirSync(directory, { mode: DIR_MODE });
      } catch (error) {
        if (error.code !== "EEXIST") return;
      }
    }
    if (realpathSync(directory) !== directory) return;
    chmodSync(directory, DIR_MODE);
    const name = basename(ctx.marker).replace(/\.pending\.json$/, "");
    const path = join(directory, `${name}-${randomUUID()}.json`);
    const fd = openSync(
      path,
      constants.O_CREAT |
        constants.O_EXCL |
        constants.O_WRONLY |
        (constants.O_NOFOLLOW ?? 0),
      FILE_MODE,
    );
    try {
      const payload = {
        timestamp: new Date().toISOString(),
        reason,
        exit_code: exitCode,
        signal,
      };
      writeFileSync(fd, `${JSON.stringify(payload)}\n`);
    } finally {
      closeSync(fd);
    }
    chmodSync(path, FILE_MODE);
  } catch {}
}

function cleanup(ctx) {
  unlinkValidated(ctx.marker, ctx.pending, ".pending.json");
  unlinkValidated(ctx.committing, ctx.pending, ".committing.json");
  unlinkValidated(ctx.source, ctx.scratch, ".jsonl");
  unlinkValidated(ctx.status, ctx.control, ".completion.json");
}

function readOutcome(ctx) {
  try {
    if (!regularNoLink(ctx.status)) return "missing-status";
    const status = JSON.parse(readFileSync(ctx.status, "utf-8"));
    if (status.outcome === "captured" || status.outcome === "dropped") {
      return status.outcome;
    }
    return "invalid-status";
  } catch {
    return "invalid-status";
  }
}

async function main() {
  let ctx;
  try {
    const { values, command } = parseArgs(process.argv.slice(2));
    ctx = validate(values);
    if (command[0] !== join(ctx.root, "factory", "scripts", "usage-capture-runtime")) {
      fail("invalid capture command");
    }
    const result = await new Promise((resolveResult) => {
      const child = spawn(command[0], command.slice(1), { cwd: ctx.root, stdio: "ignore" });
      child.once("error", (error) =>
        resolveResult({
          code: null,
          signal: null,
          reason: `launcher-spawn-${String(error.code || "failed").toLowerCase()}`,
        }),
      );
      child.once("close", (code, signal) =>
        resolveResult({
          code,
          signal,
          reason: code === 0 ? readOutcome(ctx) : "capture-process-failed",
        }),
      );
    });
    if (result.reason !== "captured") diagnostic(ctx, result.reason, result.code, result.signal);
  } catch {
    if (ctx) diagnostic(ctx, "supervisor-failed", null, null);
  } finally {
    if (ctx) cleanup(ctx);
  }
}

await main();
