#!/usr/bin/env node
/** Own Pi registration cleanup only until the Python supervisor accepts it. */
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
const DEFAULT_TIMEOUT_MS = 5000;

function fail(message) {
  throw new Error(message);
}

function regular(path) {
  const info = lstatSync(path);
  return info.isFile() && !info.isSymbolicLink();
}

function parse(argv) {
  const split = argv.indexOf("--supervisor-command");
  if (split < 0) fail("missing supervisor command");
  const values = {};
  for (let index = 0; index < split; index += 2) {
    const key = argv[index];
    const value = argv[index + 1];
    if (!key?.startsWith("--") || value === undefined) fail("invalid bootstrap arguments");
    values[key.slice(2)] = value;
  }
  return { values, command: argv.slice(split + 1) };
}

function validate(values, command) {
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
  const handshake = values.handshake;
  const status = values.status;
  if (!isAbsolute(marker) || dirname(marker) !== pending || !basename(marker).endsWith(".pending.json") || !regular(marker)) {
    fail("invalid marker");
  }
  if (!isAbsolute(source) || dirname(source) !== scratch || !basename(source).endsWith(".jsonl") || !regular(source)) {
    fail("invalid source");
  }
  const expectedHandshake = join(control, basename(marker).replace(/\.pending\.json$/, ".accepted.json"));
  const expectedStatus = join(control, basename(marker).replace(/\.pending\.json$/, ".completion.json"));
  if (handshake !== expectedHandshake || status !== expectedStatus || existsSync(handshake)) fail("invalid handshake");
  const registration = JSON.parse(readFileSync(marker, "utf-8"));
  if (registration.generation !== values.generation || registration.staged_source !== source) fail("registration mismatch");
  const launcher = join(root, "factory", "scripts", "usage-capture-runtime");
  if (command[0] !== launcher) fail("invalid supervisor launcher");
  const timeout = Number(values["accept-timeout-ms"] || DEFAULT_TIMEOUT_MS);
  if (!Number.isSafeInteger(timeout) || timeout < 1 || timeout > DEFAULT_TIMEOUT_MS) fail("invalid timeout");
  return { root, control, pending, scratch, marker, source, handshake, status, generation: values.generation, timeout };
}

function unlinkValidated(path, parent, suffix) {
  try {
    if (dirname(path) === parent && basename(path).endsWith(suffix) && regular(path)) unlinkSync(path);
  } catch {}
}

function cleanup(ctx) {
  unlinkValidated(ctx.marker, ctx.pending, ".pending.json");
  unlinkValidated(ctx.source, ctx.scratch, ".jsonl");
  unlinkValidated(ctx.handshake, ctx.control, ".accepted.json");
  unlinkValidated(ctx.status, ctx.control, ".completion.json");
}

function statePermitsDiagnostic(ctx) {
  try {
    if (realpathSync(ctx.control) !== ctx.control) return false;
    const state = JSON.parse(readFileSync(join(ctx.control, "state.json"), "utf-8"));
    return state.generation === ctx.generation && ["active", "drain"].includes(state.mode);
  } catch {
    return false;
  }
}

function diagnostic(ctx, reason, exitCode) {
  if (!statePermitsDiagnostic(ctx)) return;
  try {
    const directory = join(ctx.control, "diagnostics");
    mkdirSync(directory, { mode: DIR_MODE, recursive: false });
  } catch (error) {
    if (error.code !== "EEXIST") return;
  }
  try {
    const directory = join(ctx.control, "diagnostics");
    if (realpathSync(directory) !== directory) return;
    chmodSync(directory, DIR_MODE);
    const path = join(directory, `bootstrap-${randomUUID()}.json`);
    const fd = openSync(path, constants.O_CREAT | constants.O_EXCL | constants.O_WRONLY | (constants.O_NOFOLLOW ?? 0), FILE_MODE);
    try {
      writeFileSync(fd, `${JSON.stringify({ timestamp: new Date().toISOString(), reason, exit_code: exitCode, signal: null })}\n`);
    } finally {
      closeSync(fd);
    }
    chmodSync(path, FILE_MODE);
  } catch {}
}

function accepted(ctx) {
  try {
    if (!regular(ctx.handshake)) return false;
    const value = JSON.parse(readFileSync(ctx.handshake, "utf-8"));
    return value.accepted === true && value.generation === ctx.generation;
  } catch {
    return false;
  }
}

function cancelled(ctx) {
  try {
    const value = JSON.parse(readFileSync(join(ctx.control, "state.json"), "utf-8"));
    return value.generation !== ctx.generation || value.mode === "cancel";
  } catch {
    return true;
  }
}

async function bootstrap() {
  let ctx;
  let transferred = false;
  try {
    const { values, command } = parse(process.argv.slice(2));
    ctx = validate(values, command);
    const result = await new Promise((resolveResult) => {
      const child = spawn(command[0], command.slice(1), { cwd: ctx.root, stdio: "ignore" });
      let settled = false;
      const finish = (value) => {
        if (settled) return;
        settled = true;
        clearInterval(poll);
        clearTimeout(timeout);
        resolveResult(value);
      };
      child.once("error", (error) => finish({ reason: `launcher-spawn-${String(error.code || "failed").toLowerCase()}`, code: null }));
      child.once("close", (code) => finish({ reason: "launcher-exit-before-acceptance", code }));
      const poll = setInterval(() => {
        if (accepted(ctx)) finish({ reason: "accepted", code: null });
        else if (cancelled(ctx)) finish({ reason: "cancelled", code: null });
      }, 10);
      const timeout = setTimeout(() => finish({ reason: "acceptance-timeout", code: null }), ctx.timeout);
    });
    transferred = result.reason === "accepted";
    if (transferred) unlinkValidated(ctx.handshake, ctx.control, ".accepted.json");
    if (!transferred && result.reason !== "cancelled") diagnostic(ctx, result.reason, result.code);
  } catch {
    // Invalid/untrusted paths are never cleanup authority.
  } finally {
    if (ctx && !transferred) cleanup(ctx);
  }
}

await bootstrap();
