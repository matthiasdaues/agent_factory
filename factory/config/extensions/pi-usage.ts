/** Best-effort bridge from Pi JSON streams to the shared usage-capture CLI. */
import { execFileSync, spawn } from "node:child_process";
import {
  accessSync,
  chmodSync,
  constants,
  existsSync,
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
  const usageRoot = activeUsageRoot(cwd);
  if (!usageRuntimeReady(usageRoot)) return;
  const captureScript = join(usageRoot, "factory", "scripts", "usage-capture-runtime");
  const factoryState = join(usageRoot, ".agent-factory", "usage-control", "state.json");
  const controlDir = join(usageRoot, ".agent-factory", "usage-control");
  const pendingDir = join(usageRoot, ".agent-factory", "usage-control", "pending");
  const scratch = join(usageRoot, ".agent-factory", "usage", ".capture");
  const transcript = join(scratch, `${sessionId}-${randomUUID()}.jsonl`);
  const registrationId = `${sessionId}-${randomUUID()}`;
  const marker = join(pendingDir, `${registrationId}.pending.json`);
  const metadataTemp = join(controlDir, `${registrationId}.registration.tmp`);
  const completionStatus = join(controlDir, `${registrationId}.completion.json`);
  try {
    if (canonical(scratch) !== normalize(scratch) || canonical(pendingDir) !== normalize(pendingDir)) {
      throw new Error("usage lifecycle directories are redirected");
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
    writeFileSync(transcript, stream.endsWith("\n") ? stream : `${stream}\n`, {
      encoding: "utf-8",
      flag: "wx",
      mode: 0o600,
    });
    chmodSync(transcript, 0o600);
    requireEligibleState(factoryState, state.generation);
    accessSync(captureScript, constants.X_OK);
    const args = [
      "--cli", "pi", "--transcript", transcript, "--session", sessionId,
      "--depth", String(context.depth ?? 0),
      "--pending-marker", marker,
      "--usage-generation", state.generation,
      "--cleanup-owner", "supervisor",
      "--completion-status", completionStatus,
    ];
    if (context.parentSessionId) args.push("--parent-session", context.parentSessionId);
    if (context.agent) args.push("--agent", context.agent);
    if (context.model) args.push("--model", context.model);
    if (context.exitStatus) args.push("--exit-status", context.exitStatus);
    const child = spawn(captureScript, [
      "--lifecycle", "supervise",
      "--root", usageRoot,
      "--marker", marker,
      "--source", transcript,
      "--status", completionStatus,
      "--generation", state.generation,
      "--capture-command",
      captureScript,
      ...args,
    ], {
      cwd: usageRoot,
      stdio: "ignore",
      detached: true,
    });
    child.once("error", () => removeRegistration(marker, transcript, metadataTemp, completionStatus));
    child.unref();
  } catch (error) {
    // Usage telemetry must never affect the measured run.
    if (isHardLinkCapabilityError(error)) {
      console.error(
        "Agent Factory: Pi usage capture unavailable: the project filesystem " +
          "does not support the required same-volume hard-link registration fence.",
      );
    }
    removeRegistration(marker, transcript, metadataTemp, completionStatus);
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

function removeRegistration(marker: string, transcript: string, metadataTemp?: string, completionStatus?: string): void {
  removeStagedTranscript(marker);
  removeStagedTranscript(transcript);
  if (metadataTemp) removeStagedTranscript(metadataTemp);
  if (completionStatus) removeStagedTranscript(completionStatus);
}

function removeStagedTranscript(transcript: string): void {
  try {
    unlinkSync(transcript);
  } catch {
    // Absent/unwritable scratch is harmless at the best-effort boundary.
  }
}
