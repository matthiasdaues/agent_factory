/** Capture a human Pi session once at Pi's graceful session_shutdown boundary. */
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { activeSessionId, capturePiStream, DEPTH_ENV, INLINE_CAPTURE_ENV } from "./pi-usage.ts";

export default function (pi: ExtensionAPI) {
  if (process.env[INLINE_CAPTURE_ENV] === "1") return;
  let captured = false;

  pi.on("session_shutdown", async (_event, ctx) => {
    if (captured) return;
    captured = true;
    try {
      const manager = ctx.sessionManager;
      const sessionId = activeSessionId(manager);
      const events = manager.getBranch().map((entry: unknown) => {
        const item = entry as { type?: string; message?: unknown };
        return item.type === "message"
          ? { type: "message_end", message: item.message }
          : item;
      });
      capturePiStream(ctx.cwd, events.map((event: unknown) => JSON.stringify(event)).join("\n"), {
        sessionId,
        parentSessionId: process.env.PI_AGENT_FACTORY_PARENT_SESSION_ID,
        depth: Number.parseInt(process.env[DEPTH_ENV] || "0", 10) || 0,
        agent: "human",
        exitStatus: "success",
      });
    } catch {
      // Best-effort: shutdown must complete even with malformed session state.
    }
  });
}
