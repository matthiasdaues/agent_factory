/** Capture a human Pi session once at Pi's graceful session_shutdown boundary. */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { readFileSync, statSync } from "node:fs";
import { activeSessionId, capturePiStream, canonicalPiModel, DEPTH_ENV, INLINE_CAPTURE_ENV } from "./pi-usage.ts";

/** Read Pi's persisted session file when it is a safe, readable regular file.
 *
 * The session file holds the full event stream (system context, thinking,
 * tool calls, tool results, and assistant messages with final per-turn
 * usage), whereas `getBranch()` returns only the rendered conversation and
 * omits almost everything that makes up real token usage. Prefer the file so
 * the shared normalizer tokenizes the whole run, not a tiny fraction of it.
 */
function readSessionStream(manager: { getSessionFile(): string | undefined }): string | undefined {
  const sessionFile = manager.getSessionFile();
  if (!sessionFile) return undefined;
  try {
    const info = statSync(sessionFile);
    if (!info.isFile()) return undefined;
    return readFileSync(sessionFile, "utf-8");
  } catch {
    return undefined;
  }
}

/** Extract the last assistant `message.model` from a Pi JSONL stream.
 *
 * `PiNormalizer` resolves `model` the same way (last assistant
 * `message.model`), so this mirrors its choice to pick the canonical id for
 * the run. Returns `undefined` when no assistant model is present.
 */
function lastAssistantModel(stream: string): string | undefined {
  let model: string | undefined;
  for (const line of stream.split("\n")) {
    let event: { type?: string; message?: { role?: string; model?: unknown } };
    try {
      event = JSON.parse(line);
    } catch {
      continue;
    }
    const message = event.message;
    if (message && message.role === "assistant" && typeof message.model === "string") {
      model = message.model;
    }
  }
  return model;
}

/** Rebuild a reduced stream from the in-memory branch as a last resort. */
function branchStream(manager: { getBranch(): unknown[] }): string {
  const events = manager.getBranch().map((entry: unknown) => {
    const item = entry as { type?: string; message?: unknown };
    return item.type === "message"
      ? { type: "message_end", message: item.message }
      : item;
  });
  return events.map((event: unknown) => JSON.stringify(event)).join("\n");
}

export default function (pi: ExtensionAPI) {
  if (process.env[INLINE_CAPTURE_ENV] === "1") return;
  let captured = false;

  pi.on("session_shutdown", async (_event, ctx) => {
    if (captured) return;
    captured = true;
    try {
      const manager = ctx.sessionManager;
      const sessionId = activeSessionId(manager);
      // Prefer the persisted session file (full event stream) over the
      // reduced in-memory branch. Fall back to the branch only when no safe
      // session file is available, so the capture never blocks shutdown.
      const stream = readSessionStream(manager) ?? branchStream(manager);
      // Map Pi's provider-native model id (e.g. `z-ai/glm-5.2`) to its
      // canonical model.conf row value (`openrouter/z-ai/glm-5.2`) so the root
      // record carries the same `model` a subagent record would, and usage can
      // be grouped by `model` across both paths.
      const canonicalModel = canonicalPiModel(ctx.cwd, lastAssistantModel(stream));
      capturePiStream(ctx.cwd, stream, {
        sessionId,
        parentSessionId: process.env.PI_AGENT_FACTORY_PARENT_SESSION_ID,
        depth: Number.parseInt(process.env[DEPTH_ENV] || "0", 10) || 0,
        agent: "human",
        model: canonicalModel,
        exitStatus: "success",
      });
    } catch {
      // Best-effort: shutdown must complete even with malformed session state.
    }
  });
}
