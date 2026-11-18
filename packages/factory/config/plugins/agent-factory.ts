import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";

// The Factory plugin of OpenCode. It holds two guards, and each one only
// passes the call to its script and blocks the call when the script refuses.
// A missing script blocks the call (fail closed).
//
// OpenCode v2.2.7 loads the default export as a plugin definition: setup(ctx)
// registers each hook through ctx.tool.hook, and a hook that throws refuses
// the call with the error's message. Plugin.define of @opencode-ai/plugin
// returns its argument as it is, and a project with an installed Factory
// cannot resolve that package, so the plugin does not import it.
//
// BR-092, ADR-0035: guard-human-fields refuses a call that sets a field only
// the stakeholder writes. It gets the tool name and the tool arguments as
// OpenCode names them, plus the working directory: { cwd, toolName, input }.
const HUMAN_FIELD_TOOLS = new Set(["edit", "write", "patch", "shell", "execute"]);

// ADR-0039: block-dangerous-git.sh holds every git rule. The plugin passes it
// the command of a shell call and the JavaScript of an execute call as the
// command text: { toolName, input: { command } }.
const COMMAND_ARGUMENT: Record<string, string> = { shell: "command", execute: "code" };

type Call = { tool: string; input: unknown };
type Context = {
  location?: { directory?: string };
  tool: { hook(name: "execute.before", hook: (call: Call) => Promise<void>): unknown };
};

export default {
  id: "agent-factory",
  async setup(ctx: Context) {
    const cwd = ctx.location?.directory ?? process.cwd();
    await ctx.tool.hook("execute.before", async (call: Call) => {
      const tool = call.tool.toLowerCase();
      if (tool in COMMAND_ARGUMENT) blockDangerousGit(cwd, tool, call.input);
      if (HUMAN_FIELD_TOOLS.has(tool)) guardHumanFields(cwd, call);
    });
  },
};

function blockDangerousGit(cwd: string, tool: string, input: unknown) {
  const script = join(commonRoot(cwd), ".agent-factory", "factory", "config", "hooks", "block-dangerous-git.sh");
  if (!existsSync(script)) {
    throw new Error(`block-dangerous-git: guard script missing at ${script}; run update-factory`);
  }
  const command = (input as Record<string, unknown> | null)?.[COMMAND_ARGUMENT[tool]];
  const run = spawnSync("bash", [script], {
    cwd,
    encoding: "utf-8",
    input: JSON.stringify({ toolName: tool, input: { command: typeof command === "string" ? command : "" } }),
  });
  if (run.status === 0) return;
  throw new Error(reasonText(run, "block-dangerous-git: the guard refused the command"));
}

function guardHumanFields(cwd: string, call: Call) {
  const script = join(topLevel(cwd), ".agent-factory", "factory", "config", "hooks", "guard-human-fields");
  if (!existsSync(script)) {
    throw new Error(`guard-human-fields: guard script missing at ${script}; run update-factory`);
  }
  const run = spawnSync(script, [], {
    cwd,
    encoding: "utf-8",
    input: JSON.stringify({ cwd, toolName: call.tool, input: call.input }),
  });
  if (run.status === 0) return;
  throw new Error(`guard-human-fields: ${reasonText(run, "the guard refused the tool call")}`);
}

// The installed factory lives only in the primary checkout, so a linked
// worktree finds the git guardrail through the common git directory, as pi's
// extension block-dangerous-git.ts does.
function commonRoot(cwd: string) {
  const common = spawnSync("git", ["rev-parse", "--path-format=absolute", "--git-common-dir"], {
    cwd,
    encoding: "utf-8",
  });
  return common.status === 0 ? dirname(common.stdout.trim()) : cwd;
}

function topLevel(cwd: string) {
  const top = spawnSync("git", ["rev-parse", "--show-toplevel"], { cwd, encoding: "utf-8" });
  return top.status === 0 ? top.stdout.trim() : cwd;
}

function reasonText(run: ReturnType<typeof spawnSync<string>>, fallback: string) {
  const stderr = (run.stderr ?? "").trim();
  if (stderr) return stderr;
  if (run.error) return run.error.message;
  return fallback;
}
