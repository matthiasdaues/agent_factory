import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// ADR-0039: pi's git guardrail. The script block-dangerous-git.sh holds every
// rule; this extension only passes each bash command to it and returns its
// answer, as guard-human-fields.ts does. A missing script blocks the call.
export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;

    const script = guardScript(ctx.cwd);
    if (!existsSync(script)) {
      return blocked(`block-dangerous-git: guard script missing at ${script}; run update-factory`);
    }

    const run = spawnSync("bash", [script], {
      cwd: ctx.cwd,
      encoding: "utf-8",
      input: JSON.stringify({ toolName: event.toolName, input: event.input }),
    });
    if (run.status === 0) return;
    return blocked(reasonText(run));
  });
}

// The installed factory lives only in the primary checkout, so a linked
// worktree finds the script through the common git directory.
function guardScript(cwd: string) {
  const common = spawnSync("git", ["rev-parse", "--path-format=absolute", "--git-common-dir"], {
    cwd,
    encoding: "utf-8",
  });
  const root = common.status === 0 ? dirname(common.stdout.trim()) : cwd;
  return join(root, ".agent-factory", "factory", "config", "hooks", "block-dangerous-git.sh");
}

function reasonText(run: ReturnType<typeof spawnSync<string>>) {
  const stderr = (run.stderr ?? "").trim();
  if (stderr) return stderr;
  if (run.error) return run.error.message;
  return "block-dangerous-git: the guard refused the command";
}

function blocked(reason: string) {
  return { block: true as const, reason };
}
