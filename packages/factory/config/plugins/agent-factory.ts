import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { join } from "node:path";

import { Plugin } from "@opencode-ai/plugin";

// BR-092, ADR-0035: refuse a call that sets a field only the stakeholder
// writes. The guard script decides; this plugin only passes the call to it.
// It holds only the guard; the rest of the OpenCode integration extends it.
// Unlike step-guard, a missing guard script blocks the call (fail closed).
//
// Format handed to the guard on standard input: the tool name and the tool
// arguments as OpenCode names them, plus the working directory:
//   { cwd, toolName, input }
// The format is not yet checked against a real OpenCode session (FC-QG24).
const GUARDED_TOOLS = new Set(["edit", "write", "patch", "shell", "execute"]);

type Call = { tool: string; args: unknown };

export default Plugin.define({
  id: "agent-factory",
  setup(ctx: { directory?: string }) {
    const cwd = ctx.directory ?? process.cwd();
    return {
      "execute.before": async (call: Call) => {
        if (!GUARDED_TOOLS.has(call.tool.toLowerCase())) return;

        const script = guardScript(cwd);
        if (!existsSync(script)) {
          throw new Error(
            `guard-human-fields: guard script missing at ${script}; run update-factory`,
          );
        }

        const run = spawnSync(script, [], {
          cwd,
          encoding: "utf-8",
          input: JSON.stringify({ cwd, toolName: call.tool, input: call.args }),
        });
        if (run.status === 0) return;
        throw new Error(`guard-human-fields: ${reasonText(run)}`);
      },
    };
  },
});

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
