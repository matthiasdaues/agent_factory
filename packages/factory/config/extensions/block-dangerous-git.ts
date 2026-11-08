import { execFileSync, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";

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

    const top = git(ctx.cwd, ["rev-parse", "--show-toplevel"]);

    if (top && isCharterAllowed(top, command)) {
      return;
    }
    const gitDir = git(ctx.cwd, ["rev-parse", "--git-dir"]);
    const gitCommonDir = git(ctx.cwd, ["rev-parse", "--git-common-dir"]);

    if (createsStandaloneBranch(command)) {
      return blocked(
        "standalone branch creation is forbidden. Create the branch and its linked worktree atomically with: git worktree add -b <branch> .current-work/<feature-branch>/<branch> <base>.",
      );
    }

    if (/^git\s+worktree\s+add\s/.test(command)) {
      const wtPath = extractWorktreePath(command);
      if (wtPath && !wtPath.startsWith(".current-work/")) {
        return blocked(
          `worktrees must be created under .current-work/<feature-branch>/. Got: ${wtPath}`,
        );
      }
    }

    if (/^git\s+commit(\s|$)/.test(command)) {
      const marker = top && join(top, ".current-work", "verify-base-ok");
      if (
        top &&
        gitDir &&
        gitCommonDir &&
        gitDir !== gitCommonDir &&
        (!marker || !existsSync(marker))
      ) {
        // The installed factory lives only in the main checkout.
        const mainRoot = dirname(resolve(top, gitCommonDir));
        return blocked(
          `git commit in a worktree with no .current-work/verify-base-ok marker. Run ${join(mainRoot, ".agent-factory", "factory", "scripts", "verify-base")} <target> [--expect-base <SHA>] first.`,
        );
      }
    }

    if (/^git\s+merge\s+/.test(command)) {
      const mergeBranch = firstMergeBranch(command);
      const stop = mergeStop(ctx.cwd, top, mergeBranch);
      if (stop) return blocked(stop);
      const mergeHead = mergeBranch ? git(ctx.cwd, ["rev-parse", mergeBranch]) : null;
      const marker = top && join(top, ".current-work", "premerge-check-ok");
      const markerText = marker && existsSync(marker) ? readFileSync(marker, "utf-8") : "";
      const ok =
        !!mergeBranch &&
        !!mergeHead &&
        !!marker &&
        markerText.includes(`branch=${mergeBranch}`) &&
        markerText.includes(`head=${mergeHead}`);

      if (!ok) {
        return blocked(
          `git merge ${mergeBranch ?? "<branch>"} with no passing .current-work/premerge-check-ok marker for that branch's current head. Run .agent-factory/factory/scripts/premerge-check <target> ${mergeBranch ?? "<branch>"} first.`,
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

// BUG-0124 (BR-091): a stop denies the merge even when a premerge-check-ok
// marker from before the stop exists. The check is a read-only call to
// stop_notice. Like guard-human-fields, a gate that cannot run it fails closed.
function mergeStop(cwd: string, top: string | null, mergeBranch: string | null) {
  const name = mergeBranch ?? "<branch>";
  const scripts = join(top ?? cwd, ".agent-factory", "factory", "scripts");
  if (!existsSync(join(scripts, "dispatch_lib.py"))) {
    return `git merge ${name}: the stop check is missing at ${scripts}/dispatch_lib.py; run update-factory.`;
  }
  const run = spawnSync(
    "python3",
    [
      "-c",
      "import sys; sys.path.insert(0, sys.argv[1]); from dispatch_lib import stop_notice; sys.stdout.write(stop_notice() or '')",
      scripts,
    ],
    { cwd, encoding: "utf-8" },
  );
  if (run.status !== 0) {
    return `git merge ${name}: the stop check failed to run, so the merge is denied. Run update-factory.`;
  }
  if (run.stdout) {
    return `git merge ${name} during a stop on a critical finding; no .current-work/premerge-check-ok marker counts until the stop lifts. ${run.stdout}`;
  }
  return null;
}

function isCharterAllowed(top: string, command: string): boolean {
  const charter = join(top, "docs", "charter", "testing.yaml");
  if (!existsSync(charter)) return false;
  const text = readFileSync(charter, "utf-8");
  for (const field of ["test_command", "test_staged_command", "test_changed_command"]) {
    const match = text.match(new RegExp(`^${field}:\\s*(.+)$`, "m"));
    if (!match) continue;
    let val = match[1].trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (val && command === val) return true;
  }
  return false;
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

function extractWorktreePath(command: string) {
  const rest = command.replace(/^git\s+worktree\s+add\s+/, "");
  const tokens = rest.split(/\s+/);
  let skipNext = false;
  for (const tok of tokens) {
    if (skipNext) { skipNext = false; continue; }
    if (tok === "-b" || tok === "-B") { skipNext = true; continue; }
    if (tok.startsWith("-")) continue;
    return tok;
  }
  return null;
}

function createsStandaloneBranch(command: string) {
  return (
    /^git\s+switch\s+.*(?:^|\s)-[cC](?:\s|$)/.test(command) ||
    /^git\s+checkout\s+.*(?:^|\s)-[bB](?:\s|$)/.test(command) ||
    /^git\s+branch\s+(?:(?:--track|--copy|-c|-C)\s+)?[^-\s]\S*(?:\s+\S+)?\s*$/.test(command)
  );
}
