import { execFileSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

const DANGEROUS_PATTERNS = [
  /git push/,
  /git reset --hard/,
  /git clean -fd/,
  /git clean -f/,
  /git branch -D/,
  /git checkout \./,
  /git restore \./,
  /push --force/,
  /reset --hard/,
  /--no-verify/,
  /git\s+commit[^|&;]*\s-n(\s|$)/,
  /core\.hooksPath/,
  /pre-commit uninstall/,
  /SKIP=.*(git commit|pre-commit)/,
  /^pytest(\s|$)/,
  /^python[0-9]* -m pytest/,
  /^uv run pytest/,
  /npm test/,
  /npm run test/,
  /yarn test/,
  /^go test/,
  /^cargo test/,
  /^jest(\s|$)/,
  /^vitest(\s|$)/,
  /^mocha(\s|$)/,
];

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;

    const command = String(event.input.command ?? "");

    if (
      /^factory\/scripts\/run-tests\s+--staged(\s|$)/.test(command)
    ) {
      return;
    }

    const top = git(ctx.cwd, ["rev-parse", "--show-toplevel"]);
    const gitDir = git(ctx.cwd, ["rev-parse", "--git-dir"]);
    const gitCommonDir = git(ctx.cwd, ["rev-parse", "--git-common-dir"]);

    if (/^git\s+commit(\s|$)/.test(command)) {
      const marker = top && join(top, ".agent-factory", "verify-base-ok");
      if (
        top &&
        gitDir &&
        gitCommonDir &&
        gitDir !== gitCommonDir &&
        (!marker || !existsSync(marker))
      ) {
        return blocked(
          "git commit in a worktree with no .agent-factory/verify-base-ok marker. Run factory/scripts/verify-base <target> [--expect-base <SHA>] first.",
        );
      }
    }

    if (/^git\s+merge\s+/.test(command)) {
      const mergeBranch = firstMergeBranch(command);
      const mergeHead = mergeBranch ? git(ctx.cwd, ["rev-parse", mergeBranch]) : null;
      const marker = top && join(top, ".agent-factory", "premerge-check-ok");
      const markerText = marker && existsSync(marker) ? readFileSync(marker, "utf-8") : "";
      const ok =
        !!mergeBranch &&
        !!mergeHead &&
        !!marker &&
        markerText.includes(`branch=${mergeBranch}`) &&
        markerText.includes(`head=${mergeHead}`);

      if (!ok) {
        return blocked(
          `git merge ${mergeBranch ?? "<branch>"} with no passing .agent-factory/premerge-check-ok marker for that branch's current head. Run factory/scripts/premerge-check <target> ${mergeBranch ?? "<branch>"} first.`,
        );
      }
    }

    for (const pattern of DANGEROUS_PATTERNS) {
      if (pattern.test(command)) {
        return blocked(
          `BLOCKED: '${command}' matches dangerous pattern '${pattern.source}'. The user has prevented you from doing this.`,
        );
      }
    }
  });
}

function blocked(reason: string) {
  return { block: true as const, reason };
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

function firstMergeBranch(command: string) {
  const rest = command.replace(/^git\s+merge\s+/, "");
  for (const token of rest.split(/\s+/)) {
    if (!token || token.startsWith("-")) continue;
    return token;
  }
  return null;
}
