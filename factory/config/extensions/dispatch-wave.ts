/**
 * dispatch-wave.ts — parallel, worktree-isolated agent dispatch for Pi.
 *
 * The wave dispatcher layered on the run_agent primitive (ADR-0004, FR-J4). It
 * ports implementation-agent, whose prose depends on Claude Code's native Agent
 * tool (`isolation: "worktree"`, simultaneous subagent spawns) — capabilities
 * Pi has no equivalent of. `dispatch_wave` takes one caller-planned wave of
 * file-disjoint, dependency-satisfied items and, for each, cuts a feature
 * branch in its own git worktree, spawns a factory agent there in a separate
 * `pi` session, and — unless told not to — validates the finished branch with
 * `premerge-check` before merging it into the target branch.
 *
 * The tool deliberately does NOT plan the wave: output-file overlap and
 * dependency ordering stay with the calling agent's plan (proposal §7 Q4), the
 * same division implementation-agent already documents. A wave handed here must
 * already be parallel-safe.
 *
 * Execution order matters. Worktrees are created serially because
 * `git worktree add` takes a repository lock; agents then spawn in parallel;
 * merges run serially, each gated by its own `premerge-check`. Author/reviewer
 * independence and the git-safety guardrail hold in every child, exactly as for
 * run_agent — each child is a separate `pi` session that loads the same
 * project-local extensions.
 *
 * Symlinked to `.pi/extensions/dispatch-wave.ts` by `factory/scripts/
 * init-factory`, alongside run-agent.ts; reversed by `remove-factory`.
 *
 * See docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md and
 * docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md.
 */
import { execFileSync, spawn } from "node:child_process";
import { existsSync, mkdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { activeSessionId, capturePiStream, INLINE_CAPTURE_ENV, newSessionId, SESSION_ENV } from "./pi-usage.ts";

/** Cap on nested agent spawns, shared with run_agent (BR-035). */
const MAX_DEPTH = 3;
const DEPTH_ENV = "PI_RUN_AGENT_DEPTH";
/** The agent each wave item runs unless it names another. */
const DEFAULT_AGENT = "developer-agent";
/** Where per-item worktrees are cut, under the project's git-ignored dir. */
const WORKTREE_DIR = join(".agent-factory", "worktrees");

interface ItemResult {
  branch: string;
  agent: string;
  worktree: string | null;
  model: string;
  spawned: boolean;
  spawnExit: number | null;
  merged: boolean;
  premergeExit: number | null;
  text: string;
  error: string | null;
}

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "dispatch_wave",
    label: "Dispatch a parallel wave of factory agents",
    description:
      "Run one parallel-safe wave of factory agents, each in its own git worktree on " +
      "its own feature branch, and (unless merge=false) merge each finished branch into " +
      "`target` after `premerge-check` passes. Use this instead of calling run_agent in a " +
      "loop when several file-disjoint stories should be implemented concurrently. The " +
      "wave must already be planned: items must not touch the same output files and their " +
      "dependencies must be satisfied — dispatch_wave does not compute that ordering. Each " +
      "item's `task` is the instruction for its agent; `branch` the feature branch to cut; " +
      "`base` the SHA/ref to cut it from; `model` or `tier` selects the model; `scope` lists " +
      "the output path prefixes premerge-check should confine the diff to.",
    promptGuidelines: [
      "To implement several file-disjoint stories at once under Pi, plan the wave (group " +
        "by output-file overlap, respect dependencies) and call dispatch_wave with one " +
        "parallel-safe wave — do not spawn overlapping stories together.",
    ],
    parameters: Type.Object({
      target: Type.String({
        description:
          "Branch finished feature branches merge into (the invocation branch). The " +
          "current checkout must be on this branch for merging to happen.",
      }),
      items: Type.Array(
        Type.Object({
          task: Type.String({
            description: "Instruction handed to the agent as its first and only message.",
          }),
          branch: Type.String({ description: "Feature branch to create for this item." }),
          base: Type.String({
            description: "SHA or ref to cut the feature branch from (the declared base).",
          }),
          agent: Type.Optional(
            Type.String({ description: `Agent persona; defaults to '${DEFAULT_AGENT}'.` }),
          ),
          model: Type.Optional(Type.String({ description: "Explicit model id override." })),
          tier: Type.Optional(
            Type.String({ description: "Tier (economy|standard|strong) resolved via model.conf." }),
          ),
          scope: Type.Optional(
            Type.Array(Type.String(), {
              description: "Output path prefixes for `premerge-check --scope`.",
            }),
          ),
        }),
        { description: "The wave — one parallel-safe set of file-disjoint items." },
      ),
      merge: Type.Optional(
        Type.Boolean({
          description:
            "When false, spawn and isolate only, leaving branches for the caller to merge. " +
            "Default true: premerge-check then merge each successful branch into target.",
        }),
      ),
    }),
    async execute(_toolCallId, params, signal, _onUpdate, ctx) {
      const cwd = (ctx as { cwd: string }).cwd;

      const depth = Number.parseInt(process.env[DEPTH_ENV] ?? "0", 10) || 0;
      if (depth >= MAX_DEPTH) {
        return fatal(`recursion depth ${depth} reached the bound (${MAX_DEPTH}); refusing to dispatch.`);
      }
      if (params.items.length === 0) {
        return fatal("no items to dispatch.");
      }
      if (git(cwd, ["rev-parse", "--is-inside-work-tree"]) === null) {
        return fatal("not a git repository.");
      }

      const doMerge = params.merge !== false;
      const results: ItemResult[] = params.items.map((item) => ({
        branch: item.branch,
        agent: item.agent ?? DEFAULT_AGENT,
        worktree: null,
        model: "",
        spawned: false,
        spawnExit: null,
        merged: false,
        premergeExit: null,
        text: "",
        error: null,
      }));

      // Phase A — create every worktree serially (git worktree takes a repo lock).
      mkdirSync(join(cwd, WORKTREE_DIR), { recursive: true });
      for (let i = 0; i < params.items.length; i++) {
        const item = params.items[i];
        const r = results[i];

        const agentFile = join(cwd, "factory", "agents", `${r.agent}.md`);
        if (!existsSync(agentFile)) {
          r.error = `agent file not found: factory/agents/${r.agent}.md`;
          continue;
        }

        const resolved = resolveModel(cwd, item.model, item.tier, r.agent);
        if (resolved.error) {
          r.error = resolved.error;
          continue;
        }
        r.model = resolved.model || "(pi default)";

        const wtPath = join(cwd, WORKTREE_DIR, sanitizeBranch(item.branch));
        const add = gitResult(cwd, ["worktree", "add", "-b", item.branch, wtPath, item.base]);
        if (add.status !== 0) {
          r.error = `git worktree add failed: ${add.stderr.trim() || `exit ${add.status}`}`;
          continue;
        }
        r.worktree = wtPath;
      }

      // Phase B — spawn every prepared item's agent in parallel, each in its worktree.
      await Promise.all(
        params.items.map(async (item, i) => {
          const r = results[i];
          if (!r.worktree) return; // Phase A errored for this item.

          const persona = readFileSync(join(cwd, "factory", "agents", `${r.agent}.md`), "utf-8");
          const task = verifyBasePreamble(params.target, item.base) + item.task;
          const resolved = resolveModel(cwd, item.model, item.tier, r.agent);
          const model = resolved.model; // already validated in Phase A

          const args = ["--no-session", "-a", "--mode", "json"];
          if (model) args.push("--model", model);
          args.push("--append-system-prompt", persona, "-p", task);

          const childSessionId = newSessionId();
          const parentSessionId = activeSessionId(
            (ctx as { sessionManager?: { getSessionFile(): string | undefined } }).sessionManager,
          );
          const child = await spawnPi(args, r.worktree, depth + 1, signal, childSessionId, parentSessionId);
          capturePiStream(cwd, child.stdout, {
            sessionId: childSessionId,
            parentSessionId,
            depth: depth + 1,
            agent: r.agent,
            model: model || undefined,
            exitStatus: child.status === 0 ? "success" : "failure",
          });
          r.spawned = true;
          r.spawnExit = child.status;
          if (child.error) {
            r.error = `failed to spawn pi: ${child.error}`;
            return;
          }
          const parsed = parseFinalMessage(child.stdout);
          if (child.status !== 0 || !parsed) {
            const tail = child.stderr.trim().split("\n").slice(-10).join("\n");
            r.error = `child pi exited ${child.status} without a usable message_end.\n${tail}`;
            return;
          }
          r.text = parsed.text;
        }),
      );

      // Phase C — premerge-check then merge, serially, only for cleanly spawned items.
      if (doMerge) {
        const onTarget = git(cwd, ["rev-parse", "--abbrev-ref", "HEAD"]) === params.target;
        // Freeze the wave's common base: premerge-check runs against this SHA,
        // not the live target, so a sibling merge advancing the target does not
        // falsely flag a later branch as stale-based. Merges still land on the
        // live target branch.
        const waveBase = git(cwd, ["rev-parse", params.target]);
        for (let i = 0; i < params.items.length; i++) {
          const r = results[i];
          const item = params.items[i];
          if (r.error || r.spawnExit !== 0) continue;
          if (!onTarget || !waveBase) {
            r.error = `not merged: checkout is not on target branch '${params.target}'.`;
            continue;
          }
          const pmArgs = [waveBase, item.branch];
          for (const s of item.scope ?? []) pmArgs.push("--scope", s);
          const pm = runScript(cwd, "premerge-check", pmArgs);
          r.premergeExit = pm.status;
          if (pm.status !== 0) {
            r.error = `premerge-check blocked the merge (exit ${pm.status}): ${pm.stderr.trim() || pm.stdout.trim()}`;
            continue;
          }
          const merge = gitResult(cwd, ["merge", "--no-ff", item.branch]);
          if (merge.status !== 0) {
            r.error = `git merge failed: ${merge.stderr.trim() || `exit ${merge.status}`}`;
            continue;
          }
          r.merged = true;
          // Merged cleanly — retire the worktree; leave failed ones for inspection.
          if (r.worktree) gitResult(cwd, ["worktree", "remove", "--force", r.worktree]);
        }
      }

      return {
        content: [{ type: "text" as const, text: summarize(results, doMerge) }],
        details: { target: params.target, merge: doMerge, items: results },
      };
    },
  });
}

/** The verify-base preamble every worktree-isolated dispatch must open with. */
function verifyBasePreamble(target: string, base: string): string {
  return (
    `Before any other work, run \`factory/scripts/verify-base ${target} --expect-base ${base}\`. ` +
    `If it exits non-zero, stop: do not read, edit, or commit — report the printed diagnosis. ` +
    `Only once it passes, proceed with the task below.\n\n`
  );
}

/** Resolve the model: explicit id > tier via resolve-model > agent's own tier. */
function resolveModel(
  cwd: string,
  model: string | undefined,
  tier: string | undefined,
  agent: string,
): { model: string; error?: string } {
  if (model) return { model };
  const script = join(cwd, "factory", "scripts", "resolve-model");
  const args = tier
    ? ["--tier", tier, "--cli", "pi"]
    : ["--agent", agent, "--cli", "pi", "--agents-dir", join(cwd, "factory", "agents")];
  args.push("--model-conf", join(cwd, "config", "model.conf"));
  try {
    const out = execFileSync(script, args, { cwd, encoding: "utf-8", stdio: ["ignore", "pipe", "pipe"] });
    return { model: out.trim() };
  } catch (err) {
    const e = err as { stderr?: string; message?: string };
    const reason = (e.stderr ?? e.message ?? "resolve-model failed").trim();
    return { model: "", error: reason.replace(/^resolve-model:\s*/, "") };
  }
}

interface SpawnResult {
  status: number | null;
  stdout: string;
  stderr: string;
  error: string | null;
}

/** Spawn a child `pi` asynchronously, capturing stdout/stderr. */
function spawnPi(
  args: string[],
  cwd: string,
  childDepth: number,
  signal: AbortSignal,
  sessionId: string,
  parentSessionId?: string,
): Promise<SpawnResult> {
  return new Promise((resolve) => {
    const child = spawn("pi", args, {
      cwd,
      signal,
      env: {
        ...process.env,
        [DEPTH_ENV]: String(childDepth),
        [SESSION_ENV]: sessionId,
        PI_AGENT_FACTORY_PARENT_SESSION_ID: parentSessionId || "",
        [INLINE_CAPTURE_ENV]: "1",
      },
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (d) => (stdout += d.toString()));
    child.stderr.on("data", (d) => (stderr += d.toString()));
    child.on("error", (err) => resolve({ status: null, stdout, stderr, error: err.message }));
    child.on("close", (code) => resolve({ status: code, stdout, stderr, error: null }));
  });
}

interface FinalMessage {
  text: string;
  usage: unknown;
}

/** Last assistant message_end's concatenated text, from a `--mode json` stream. */
function parseFinalMessage(stdout: string): FinalMessage | null {
  let last: FinalMessage | null = null;
  for (const line of stdout.split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed[0] !== "{") continue;
    let event: { type?: string; message?: { role?: string; content?: unknown[]; usage?: unknown } };
    try {
      event = JSON.parse(trimmed);
    } catch {
      continue;
    }
    if (event.type !== "message_end" || !event.message) continue;
    if (event.message.role && event.message.role !== "assistant") continue;
    const text = (event.message.content ?? [])
      .filter((c): c is { type: string; text: string } => {
        const part = c as { type?: string; text?: unknown };
        return part.type === "text" && typeof part.text === "string";
      })
      .map((c) => c.text)
      .join("");
    last = { text, usage: event.message.usage ?? null };
  }
  return last;
}

/** Run a factory script synchronously, returning status and captured output. */
function runScript(cwd: string, name: string, args: string[]) {
  const script = join(cwd, "factory", "scripts", name);
  try {
    const stdout = execFileSync(script, args, { cwd, encoding: "utf-8", stdio: ["ignore", "pipe", "pipe"] });
    return { status: 0, stdout, stderr: "" };
  } catch (err) {
    const e = err as { status?: number; stdout?: string; stderr?: string; message?: string };
    return { status: e.status ?? 1, stdout: e.stdout ?? "", stderr: e.stderr ?? e.message ?? "" };
  }
}

/** Run git, returning trimmed stdout or null on failure. */
function git(cwd: string, args: string[]): string | null {
  const r = gitResult(cwd, args);
  return r.status === 0 ? r.stdout.trim() : null;
}

function gitResult(cwd: string, args: string[]) {
  try {
    const stdout = execFileSync("git", args, { cwd, encoding: "utf-8", stdio: ["ignore", "pipe", "pipe"] });
    return { status: 0, stdout, stderr: "" };
  } catch (err) {
    const e = err as { status?: number; stdout?: string; stderr?: string; message?: string };
    return { status: e.status ?? 1, stdout: e.stdout ?? "", stderr: e.stderr ?? e.message ?? "" };
  }
}

/** A filesystem-safe worktree directory name from a branch name. */
function sanitizeBranch(branch: string): string {
  return branch.replace(/[^A-Za-z0-9._-]/g, "-");
}

/** A model-legible one-line-per-item summary. */
function summarize(results: ItemResult[], doMerge: boolean): string {
  const lines = results.map((r) => {
    const state = r.error
      ? `ERROR ${r.error.split("\n")[0]}`
      : doMerge
        ? r.merged
          ? "merged"
          : "spawned, not merged"
        : "spawned";
    return `${r.branch} [${r.agent} @ ${r.model}]: ${state}`;
  });
  const merged = results.filter((r) => r.merged).length;
  const errored = results.filter((r) => r.error).length;
  const header = `dispatch_wave: ${results.length} item(s), ${merged} merged, ${errored} errored.`;
  return [header, ...lines].join("\n");
}

/** A fatal, whole-wave error result (no isError field exists on tool results). */
function fatal(reason: string) {
  return {
    content: [{ type: "text" as const, text: `dispatch_wave error: ${reason}` }],
    details: { error: true, reason },
  };
}
