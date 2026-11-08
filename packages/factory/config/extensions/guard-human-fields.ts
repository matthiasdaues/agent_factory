import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// BR-092, ADR-0035: refuse a call that sets a field only the stakeholder
// writes. The guard script decides; this extension only passes the call to it.
// Unlike step-guard.ts, a missing guard script blocks the call (fail closed).
const GUARDED_TOOLS = new Set(["edit", "write", "apply_patch", "bash"]);

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (!GUARDED_TOOLS.has(event.toolName.toLowerCase())) return;

    const script = guardScript(ctx.cwd);
    if (!existsSync(script)) {
      return blocked(
        `guard-human-fields: guard script missing at ${script}; run update-factory`,
      );
    }

    const run = spawnSync(script, [], {
      cwd: ctx.cwd,
      encoding: "utf-8",
      input: JSON.stringify({ toolName: event.toolName, input: event.input }),
    });
    if (run.status === 0) return;
    return blocked(`guard-human-fields: ${reasonText(run)}`);
  });
}

function guardScript(cwd: string) {
  const top = spawnSync("git", ["rev-parse", "--show-toplevel"], {
    cwd,
    encoding: "utf-8",
  });
  const root = top.status === 0 ? top.stdout.trim() : cwd;
  return join(root, ".agent-factory", "factory", "config", "hooks", "guard-human-fields");
}

function reasonText(run: ReturnType<typeof spawnSync<string>>) {
  const stderr = (run.stderr ?? "").trim();
  if (stderr) return stderr;
  if (run.error) return run.error.message;
  return "the guard refused the tool call";
}

function blocked(reason: string) {
  return { block: true as const, reason };
}
