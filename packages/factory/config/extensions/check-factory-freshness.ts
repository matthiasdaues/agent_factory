import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  let checked = false;

  pi.on("tool_call", async (_event, ctx) => {
    if (checked) return;
    checked = true;

    const top = git(ctx.cwd, ["rev-parse", "--show-toplevel"]);
    if (!top) return;

    const sourceDir = join(top, "packages", "factory");
    if (!existsSync(sourceDir)) return;

    const manifestPath = join(top, ".agent-factory", "factory-install.json");
    if (!existsSync(manifestPath)) return;

    const currentHash = git(top, ["rev-parse", "HEAD:packages/factory"]);
    if (!currentHash) return;

    let recordedHash = "";
    try {
      const manifest = JSON.parse(readFileSync(manifestPath, "utf-8"));
      recordedHash = manifest.factory_tree_hash ?? "";
    } catch {
      return;
    }

    if (recordedHash && currentHash === recordedHash) return;

    console.error(
      "WARNING: installed factory/ is out of sync with packages/factory/. " +
        "To update, run: ./init-factory --update .",
    );
  });
}

function git(cwd: string, args: string[]) {
  try {
    return execFileSync("git", args, {
      cwd,
      encoding: "utf8",
      stdio: ["ignore", "pipe", "ignore"],
    }).trim();
  } catch {
    return null;
  }
}
