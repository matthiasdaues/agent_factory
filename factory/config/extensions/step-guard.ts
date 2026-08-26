import { execFileSync } from "node:child_process";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    const guardType = inferGuardType(event.toolName);
    if (!guardType) return;

    const script = projectScript(ctx.cwd);
    if (!script) return;

    const payload = normalizeEvent(guardType, event.input);

    try {
      execFileSync(script, ["--guard-type", guardType], {
        cwd: ctx.cwd,
        encoding: "utf-8",
        input: JSON.stringify(payload),
        stdio: ["pipe", "pipe", "pipe"],
      });
    } catch (error) {
      return blocked(`step-guard ${guardType}: ${stderrText(error)}`);
    }
  });
}

function inferGuardType(toolName: string) {
  switch (toolName.toLowerCase()) {
    case "read":
    case "view":
    case "read_file":
      return "read";
    case "edit":
    case "write":
    case "write_file":
    case "create":
      return "write";
    case "bash":
      return "bash";
    default:
      return null;
  }
}

function projectScript(cwd: string) {
  try {
    const root = execFileSync("git", ["rev-parse", "--show-toplevel"], {
      cwd,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
    return join(root, "factory", "scripts", "step-guard");
  } catch {
    return null;
  }
}

function normalizeEvent(guardType: string, input: unknown) {
  if (guardType === "bash") {
    return { command: readString(input, ["command", "cmd"]) };
  }
  return { path: readString(input, ["filePath", "file_path", "path"]) };
}

function readString(input: unknown, keys: string[]) {
  const value = input as Record<string, unknown> | undefined;
  if (!value) return "";
  for (const key of keys) {
    const current = value[key];
    if (typeof current === "string") return current;
  }
  return "";
}

function stderrText(error: unknown) {
  if (
    error &&
    typeof error === "object" &&
    "stderr" in error &&
    typeof (error as { stderr?: unknown }).stderr === "string"
  ) {
    const stderr = (error as { stderr: string }).stderr.trim();
    if (stderr) return stderr;
  }
  if (error instanceof Error && error.message) return error.message;
  return "step-guard denied the tool call";
}

function blocked(reason: string) {
  return { block: true as const, reason };
}
