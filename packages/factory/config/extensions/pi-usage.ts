/** Best-effort bridge from Pi JSON streams to the shared usage-capture CLI. */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { execFileSync, spawn } from "node:child_process";
import {
  accessSync,
  chmodSync,
  constants,
  closeSync,
  existsSync,
  openSync,
  linkSync,
  readFileSync,
  realpathSync,
  renameSync,
  unlinkSync,
  writeFileSync,
} from "node:fs";
import { randomUUID } from "node:crypto";
import { basename, dirname, isAbsolute, join, normalize, resolve } from "node:path";

export const SESSION_ENV = "PI_AGENT_FACTORY_SESSION_ID";
export const DEPTH_ENV = "PI_RUN_AGENT_DEPTH";
export const INLINE_CAPTURE_ENV = "PI_AGENT_FACTORY_INLINE_CAPTURE";
export const USAGE_ROOT_ENV = "PI_AGENT_FACTORY_USAGE_ROOT";

export interface PiCaptureContext {
  sessionId?: string;
  parentSessionId?: string;
  depth?: number;
  agent?: string;
  model?: string;
  exitStatus?: string;
}

interface PiSessionManager {
  getSessionFile(): string | undefined;
}

let fallbackSessionId: string | undefined;
let cachedUsageRoot: string | undefined;

export function newSessionId(): string {
  return `pi-${randomUUID()}`;
}

/** Resolve the current Pi session consistently at tool and shutdown boundaries. */
export function activeSessionId(sessionManager?: PiSessionManager): string {
  const sessionFile = sessionManager?.getSessionFile();
  if (sessionFile) return basename(sessionFile, ".jsonl");
  if (process.env[SESSION_ENV]) return process.env[SESSION_ENV];
  fallbackSessionId ??= newSessionId();
  return fallbackSessionId;
}

/** Map a Pi-reported model id to its canonical model.conf row value.
 *
 * Pi's session file and live stream report the provider-native model id
 * (e.g. `z-ai/glm-5.2`), which may or may not carry the OpenRouter prefix
 * that model.conf stores as the row value (`openrouter/z-ai/glm-5.2`). The
 * subagent path passes the model.conf id via `--model`, so its record carries
 * the canonical id; the root path must attribute the same canonical id so
 * usage can be grouped by `model` across both paths instead of splitting one
 * model in two.
 *
 * Reads `config/model.conf` under *root* and returns the `pi.*` row value
 * whose configured id matches *reported* exactly, or whose configured id
 * shares the same final path segment (the part after the last `/`) as
 * *reported*. Returns *reported* unchanged when no `pi.*` row matches, so
 * attribution never goes null for a model configured outside model.conf.
 */
export function canonicalPiModel(root: string, reported: string | undefined): string | undefined {
  if (!reported) return reported;
  const confPath = join(root, "config", "model.conf");
  let text: string;
  try {
    text = readFileSync(confPath, "utf-8");
  } catch {
    return reported;
  }
  const reportedSuffix = reported.split("/").pop() ?? reported;
  let exact: string | undefined;
  let suffix: string | undefined;
  for (const line of text.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed.startsWith("pi.") || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq < 0) continue;
    const value = trimmed.slice(eq + 1).trim();
    if (!value) continue;
    if (value === reported) {
      exact = value;
      break;
    }
    if (!suffix && (value.split("/").pop() ?? value) === reportedSuffix) {
      suffix = value;
    }
  }
  return exact ?? suffix ?? reported;
}

/**
 * Resolve one persistent consumer root for the complete Pi process tree.
 *
 * Linked worktrees share the primary checkout's git common directory.  That
 * makes its parent a stable persistence root even after a dispatch worktree is
 * removed.  An inherited value is accepted only when it agrees with this
 * independently derived root, preventing environment-controlled executable
 * selection or telemetry redirection.
 */
export function activeUsageRoot(cwd: string): string {
  if (cachedUsageRoot) return cachedUsageRoot;
  const absoluteCwd = canonical(resolve(cwd));
  const derived = gitPrimaryRoot(absoluteCwd);
  const inherited = trustedInheritedRoot(process.env[USAGE_ROOT_ENV], derived, absoluteCwd);
  cachedUsageRoot = inherited ?? derived ?? absoluteCwd;
  process.env[USAGE_ROOT_ENV] = cachedUsageRoot;
  return cachedUsageRoot;
}

function trustedInheritedRoot(
  value: string | undefined,
  derived: string | undefined,
  cwd: string,
): string | undefined {
  if (!value || value.includes("\0") || !isAbsolute(value) || normalize(value) !== value) {
    return undefined;
  }
  const candidate = canonical(value);
  if (derived && candidate !== derived) return undefined;
  if (!derived && candidate !== cwd) return undefined;
  if (!existsSync(join(candidate, ".agent-factory", "factory-install.json"))) return undefined;
  if (!existsSync(join(candidate, "factory", "scripts", "usage-capture"))) return undefined;
  return candidate;
}

function gitPrimaryRoot(cwd: string): string | undefined {
  try {
    const common = execFileSync(
      "git",
      ["rev-parse", "--path-format=absolute", "--git-common-dir"],
      { cwd, encoding: "utf-8", stdio: ["ignore", "pipe", "ignore"] },
    ).trim();
    if (!common || !isAbsolute(common)) return undefined;
    const root = canonical(dirname(common));
    return existsSync(join(root, "factory", "scripts", "usage-capture")) ? root : undefined;
  } catch {
    return undefined;
  }
}

function gitContext(cwd: string, args: string[]): string | undefined {
  try {
    const value = execFileSync("git", args, {
      cwd,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    return value || undefined;
  } catch {
    return undefined;
  }
}

function canonical(path: string): string {
  try {
    return realpathSync(path);
  } catch {
    return normalize(path);
  }
}

/** Durably stage one stream and detach persistence from the measured run. */
export function capturePiStream(cwd: string, stream: string, context: PiCaptureContext): void {
  if (!stream.trim()) return;
  const sessionId = context.sessionId || newSessionId();
  const transcript = createPiCaptureFile(cwd, sessionId);
  if (!transcript) return;
  try {
    writeFileSync(transcript, stream.endsWith("\n") ? stream : `${stream}\n`, {
      encoding: "utf-8",
      flag: "w",
      mode: 0o600,
    });
    capturePiFile(cwd, transcript, context);
  } catch {
    removeRegistration("", transcript);
  }
}

/** Allocate a protected raw-stream handoff owned by the Pi capture bridge. */
export function createPiCaptureFile(cwd: string, sessionId: string): string | undefined {
  const usageRoot = activeUsageRoot(cwd);
  if (!usageRuntimeReady(usageRoot)) return undefined;
  const scratch = join(usageRoot, ".agent-factory", "usage", ".capture");
  const transcript = join(scratch, `${sessionId}-${randomUUID()}.jsonl`);
  try {
    if (canonical(scratch) !== normalize(scratch)) {
      throw new Error("usage lifecycle directory is redirected");
    }
    closeSync(openSync(transcript, "wx", 0o600));
    chmodSync(transcript, 0o600);
    return transcript;
  } catch {
    removeRegistration("", transcript);
    return undefined;
  }
}

/**
 * Register a complete protected JSONL file for detached, best-effort capture.
 *
 * The caller relinquishes ownership regardless of whether registration
 * succeeds; failures remove the staged file and never affect the measured run.
 */
export function capturePiFile(
  cwd: string,
  transcript: string,
  context: PiCaptureContext,
): void {
  const sessionId = context.sessionId || newSessionId();
  const usageRoot = activeUsageRoot(cwd);
  if (!usageRuntimeReady(usageRoot)) {
    removeRegistration("", transcript);
    return;
  }
  const captureScript = join(usageRoot, "factory", "scripts", "usage-capture-runtime");
  const bootstrapScript = join(usageRoot, "factory", "scripts", "pi-capture-bootstrap.mjs");
  const factoryState = join(usageRoot, ".agent-factory", "usage-control", "state.json");
  const controlDir = join(usageRoot, ".agent-factory", "usage-control");
  const pendingDir = join(usageRoot, ".agent-factory", "usage-control", "pending");
  const scratch = join(usageRoot, ".agent-factory", "usage", ".capture");
  const registrationId = `${sessionId}-${randomUUID()}`;
  const marker = join(pendingDir, `${registrationId}.pending.json`);
  const metadataTemp = join(controlDir, `${registrationId}.registration.tmp`);
  const completionStatus = join(controlDir, `${registrationId}.completion.json`);
  const acceptanceHandshake = join(controlDir, `${registrationId}.accepted.json`);
  try {
    if (canonical(scratch) !== normalize(scratch) || canonical(pendingDir) !== normalize(pendingDir)) {
      throw new Error("usage lifecycle directories are redirected");
    }
    if (dirname(transcript) !== scratch || canonical(transcript) !== normalize(transcript)) {
      throw new Error("capture source is outside the protected staging directory");
    }
    // The hard link atomically snapshots the state inode and makes this
    // registration visible in one filesystem operation. It therefore orders
    // unambiguously before or after remove-factory's atomic state replacement.
    linkSync(factoryState, marker);
    const state = readActiveState(marker);
    writeFileSync(
      metadataTemp,
      JSON.stringify({
        generation: state.generation,
        staged_source: transcript,
        session_id: sessionId,
        created_at: new Date().toISOString(),
      }) + "\n",
      { encoding: "utf-8", flag: "wx", mode: 0o600 },
    );
    chmodSync(metadataTemp, 0o600);
    // Atomically replace snapshot contents without a visibility gap in the
    // pending registry.
    renameSync(metadataTemp, marker);
    requireEligibleState(factoryState, state.generation);
    chmodSync(transcript, 0o600);
    requireEligibleState(factoryState, state.generation);
    accessSync(captureScript, constants.X_OK);
    accessSync(bootstrapScript, constants.R_OK);
    const args = [
      "--cli", "pi", "--transcript", transcript, "--session", sessionId,
      "--depth", String(context.depth ?? 0),
      "--pending-marker", marker,
      "--usage-generation", state.generation,
      "--cleanup-owner", "supervisor",
      "--completion-status", completionStatus,
    ];
    const branch = gitContext(cwd, ["symbolic-ref", "--quiet", "--short", "HEAD"]);
    const commitId = gitContext(cwd, ["rev-parse", "--verify", "HEAD"]);
    if (branch) args.push("--branch", branch);
    if (commitId) args.push("--commit", commitId);
    if (context.parentSessionId) args.push("--parent-session", context.parentSessionId);
    if (context.agent) args.push("--agent", context.agent);
    if (context.model) args.push("--model", context.model);
    if (context.exitStatus) args.push("--exit-status", context.exitStatus);
    const child = spawn(process.execPath, [
      bootstrapScript,
      "--root", usageRoot,
      "--marker", marker,
      "--source", transcript,
      "--status", completionStatus,
      "--handshake", acceptanceHandshake,
      "--generation", state.generation,
      "--supervisor-command",
      captureScript,
      "--lifecycle", "supervise",
      "--root", usageRoot,
      "--marker", marker,
      "--source", transcript,
      "--status", completionStatus,
      "--generation", state.generation,
      "--acceptance-handshake", acceptanceHandshake,
      "--capture-command",
      captureScript,
      ...args,
    ], {
      cwd: usageRoot,
      stdio: "ignore",
      detached: true,
    });
    child.once("error", () => removeRegistration(marker, transcript, metadataTemp, completionStatus, acceptanceHandshake));
    child.unref();
  } catch (error) {
    // Usage telemetry must never affect the measured run.
    if (isHardLinkCapabilityError(error)) {
      console.error(
        "Agent Factory: Pi usage capture unavailable: the project filesystem " +
          "does not support the required same-volume hard-link registration fence.",
      );
    }
    removeRegistration(marker, transcript, metadataTemp, completionStatus, acceptanceHandshake);
  }
}

function usageRuntimeReady(root: string): boolean {
  const runtime = join(root, ".agent-factory", "usage-runtime");
  return existsSync(join(runtime, ".requirements-sha256")) &&
    (existsSync(join(runtime, "bin", "python")) || existsSync(join(runtime, "Scripts", "python.exe"))) &&
    existsSync(join(root, "factory", "scripts", "usage-capture-runtime"));
}

interface UsageState {
  mode: string;
  generation: string;
}

function readActiveState(path: string): UsageState {
  const state = JSON.parse(readFileSync(path, "utf-8")) as UsageState;
  if (state.mode !== "active" || !state.generation) throw new Error("usage removal in progress");
  return state;
}

function requireEligibleState(path: string, generation: string): void {
  const state = JSON.parse(readFileSync(path, "utf-8")) as UsageState;
  if (state.generation !== generation || !["active", "drain"].includes(state.mode)) {
    throw new Error("usage installation generation changed or was cancelled");
  }
}

function isHardLinkCapabilityError(error: unknown): boolean {
  const code =
    error && typeof error === "object" && "code" in error ? String(error.code) : "";
  return ["EACCES", "EPERM", "EXDEV", "ENOTSUP", "EOPNOTSUPP"].includes(code);
}

function removeRegistration(marker: string, transcript: string, metadataTemp?: string, completionStatus?: string, acceptanceHandshake?: string): void {
  removeStagedTranscript(marker);
  removeStagedTranscript(transcript);
  if (metadataTemp) removeStagedTranscript(metadataTemp);
  if (completionStatus) removeStagedTranscript(completionStatus);
  if (acceptanceHandshake) removeStagedTranscript(acceptanceHandshake);
}

function removeStagedTranscript(transcript: string): void {
  try {
    unlinkSync(transcript);
  } catch {
    // Absent/unwritable scratch is harmless at the best-effort boundary.
  }
}

/**
 * Pi auto-loads every top-level module in `.pi/extensions`.
 *
 * This module primarily provides shared helpers to the capture and invocation
 * extensions, but it must still satisfy Pi's extension-factory contract.
 */
export default function (_pi: ExtensionAPI): void {}
