import { execFileSync } from "node:child_process";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    const guardType = inferGuardType(event.toolName);
    if (!guardType) return;

    const script = projectScript(ctx.cwd);
    if (!script) return;

    const payloads = normalizeEvent(guardType, event.input);

    for (const payload of payloads) {
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
    case "apply_patch":
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

const PATCH_HEADER_RE = /^\*{3} (?:Add|Update|Delete) File: (.+)$/gm;

function extractPatchPaths(patch: string): string[] {
  const paths: string[] = [];
  let match: RegExpExecArray | null;
  while ((match = PATCH_HEADER_RE.exec(patch)) !== null) {
    paths.push(match[1].trim());
  }
  PATCH_HEADER_RE.lastIndex = 0;
  return paths;
}

function normalizeEvent(
  guardType: string,
  input: unknown,
): Array<Record<string, string>> {
  if (guardType === "bash") {
    return [{ command: readString(input, ["command", "cmd"]) }];
  }
  const path = readString(input, ["filePath", "file_path", "path"]);
  if (path) return [{ path }];

  const patch = readString(input, ["patch"]);
  if (patch) {
    const paths = extractPatchPaths(patch);
    if (paths.length > 0) return paths.map((p) => ({ path: p }));
  }
  return [{ path: "" }];
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
