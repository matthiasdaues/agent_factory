/** Best-effort bridge from Pi JSON streams to the shared usage-capture CLI. */
import { spawnSync } from "node:child_process";
import { mkdirSync, unlinkSync, writeFileSync } from "node:fs";
import { randomUUID } from "node:crypto";
import { basename, join } from "node:path";

export const SESSION_ENV = "PI_AGENT_FACTORY_SESSION_ID";
export const DEPTH_ENV = "PI_RUN_AGENT_DEPTH";
export const INLINE_CAPTURE_ENV = "PI_AGENT_FACTORY_INLINE_CAPTURE";

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

/** Capture exactly one stream. Errors are deliberately swallowed. */
export function capturePiStream(cwd: string, stream: string, context: PiCaptureContext): void {
  if (!stream.trim()) return;
  const sessionId = context.sessionId || newSessionId();
  const scratch = join(cwd, ".agent-factory", "usage", ".capture");
  const transcript = join(scratch, `${sessionId}-${randomUUID()}.jsonl`);
  try {
    mkdirSync(scratch, { recursive: true });
    writeFileSync(transcript, stream.endsWith("\n") ? stream : `${stream}\n`, "utf-8");
    const args = [
      "--cli", "pi", "--transcript", transcript, "--session", sessionId,
      "--depth", String(context.depth ?? 0),
    ];
    if (context.parentSessionId) args.push("--parent-session", context.parentSessionId);
    if (context.agent) args.push("--agent", context.agent);
    if (context.model) args.push("--model", context.model);
    if (context.exitStatus) args.push("--exit-status", context.exitStatus);
    spawnSync(join(cwd, "factory", "scripts", "usage-capture"), args, {
      cwd,
      encoding: "utf-8",
      stdio: "ignore",
      timeout: 30_000,
    });
  } catch {
    // Usage telemetry must never affect the measured run.
  } finally {
    try { unlinkSync(transcript); } catch { /* absent/unwritable scratch is harmless */ }
  }
}
