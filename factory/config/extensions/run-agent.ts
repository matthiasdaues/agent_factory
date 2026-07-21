/**
 * run-agent.ts — the Pi invocation layer for factory agents.
 *
 * Pi has no native subagent concept, so a factory agent cannot run in a
 * separate Pi session the way Claude Code spawns a subagent. This extension
 * registers one model-callable tool, `run_agent`, that spawns a genuinely
 * separate `pi` subprocess with the agent's markdown as its system prompt and
 * returns the child's result. The separate session is what preserves
 * author/reviewer independence: the reviewer never sees the author's reasoning.
 *
 * Symlinked to `.pi/extensions/run-agent.ts` by `factory/scripts/init-factory`,
 * the same pattern the git-safety guardrail uses. Reversed by `remove-factory`.
 *
 * See docs/adr/0004-pi-subagent-invocation-via-subprocess-spawn.md and
 * docs/spec/use_cases/UC-10-invoke-a-factory-agent-under-pi.md.
 */
import { execFileSync, spawnSync } from "node:child_process";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import { activeSessionId, capturePiStream, INLINE_CAPTURE_ENV, newSessionId, SESSION_ENV } from "./pi-usage.ts";

/** Cap on nested run_agent spawns (BR-035). */
const MAX_DEPTH = 3;
const DEPTH_ENV = "PI_RUN_AGENT_DEPTH";

export default function (pi: ExtensionAPI) {
  pi.registerTool({
    name: "run_agent",
    label: "Run factory agent",
    description:
      "Run a factory agent (factory/agents/<agent>.md) in a separate, throwaway `pi` " +
      "session and return its result. Use this instead of reading an agent file and " +
      "role-playing it in the current session: the separate session preserves " +
      "author/reviewer independence (the reviewer never sees the author's reasoning). " +
      "`agent` is the agent name without `.md`; `task` is the instruction to give it; " +
      "`model` optionally overrides the tier-resolved model.",
    promptGuidelines: [
      "To run a factory agent (e.g. a reviewer over an author's artifact), call " +
        "run_agent — do not read .pi/agents/<name>.md and act it out in this session.",
    ],
    parameters: Type.Object({
      agent: Type.String({
        description: "Agent name, e.g. 'spec-review-agent' (resolves factory/agents/<agent>.md).",
      }),
      task: Type.String({
        description: "The task or prompt to hand the agent as its first and only message.",
      }),
      model: Type.Optional(
        Type.String({
          description: "Optional model id override; otherwise resolved from model.conf pi.<tier>.",
        }),
      ),
    }),
    async execute(_toolCallId, params, signal, _onUpdate, ctx) {
      const cwd = (ctx as { cwd: string }).cwd;
      const agentFile = join(cwd, "factory", "agents", `${params.agent}.md`);
      if (!existsSync(agentFile)) {
        return errorResult(
          params.agent,
          `agent file not found: factory/agents/${params.agent}.md`,
        );
      }

      // Recursion bound (BR-035): the child also loads this extension.
      const depth = Number.parseInt(process.env[DEPTH_ENV] ?? "0", 10) || 0;
      if (depth >= MAX_DEPTH) {
        return errorResult(
          params.agent,
          `recursion depth ${depth} reached the bound (${MAX_DEPTH}); refusing to spawn.`,
        );
      }

      // Resolve the model: explicit arg > model.conf pi.<tier> (via the shared
      // Python resolver, so model.conf keeps one parser — ADR-0004).
      let model = params.model;
      if (!model) {
        const resolved = resolveModel(cwd, params.agent);
        if (resolved.error) {
          return errorResult(params.agent, resolved.error);
        }
        model = resolved.model; // may be "" when on_missing=auto → let pi default
      }

      const persona = readFileSync(agentFile, "utf-8");
      const args = ["--no-session", "-a", "--mode", "json"];
      if (model) {
        args.push("--model", model);
      }
      args.push("--append-system-prompt", persona, "-p", params.task);

      const childSessionId = newSessionId();
      const parentSessionId = activeSessionId(
        (ctx as { sessionManager?: { getSessionFile(): string | undefined } }).sessionManager,
      );
      const child = spawnSync("pi", args, {
        cwd,
        encoding: "utf-8",
        maxBuffer: 64 * 1024 * 1024,
        signal,
        env: {
          ...process.env,
          [DEPTH_ENV]: String(depth + 1),
          [SESSION_ENV]: childSessionId,
          PI_AGENT_FACTORY_PARENT_SESSION_ID: parentSessionId || "",
          [INLINE_CAPTURE_ENV]: "1",
        },
      });

      capturePiStream(cwd, child.stdout ?? "", {
        sessionId: childSessionId,
        parentSessionId,
        depth: depth + 1,
        agent: params.agent,
        model: model || undefined,
        exitStatus: child.status === 0 ? "success" : "failure",
      });

      if (child.error) {
        return errorResult(params.agent, `failed to spawn pi: ${child.error.message}`);
      }

      const parsed = parseFinalMessage(child.stdout ?? "");
      if (child.status !== 0 || !parsed) {
        const stderrTail = (child.stderr ?? "").trim().split("\n").slice(-20).join("\n");
        return errorResult(
          params.agent,
          `child pi exited ${child.status} without a usable message_end.\nstderr tail:\n${stderrTail}`,
        );
      }

      return {
        content: [{ type: "text" as const, text: parsed.text }],
        details: {
          agent: params.agent,
          model: model || "(pi default)",
          usage: parsed.usage,
          exitCode: child.status,
        },
      };
    },
  });
}

/** Shell the shared Python tier resolver. Returns {model} or {error}. */
function resolveModel(cwd: string, agent: string): { model?: string; error?: string } {
  const script = join(cwd, "factory", "scripts", "resolve-model");
  try {
    const out = execFileSync(
      script,
      [
        "--agent",
        agent,
        "--cli",
        "pi",
        "--model-conf",
        join(cwd, "config", "model.conf"),
        "--agents-dir",
        join(cwd, "factory", "agents"),
      ],
      { cwd, encoding: "utf-8", stdio: ["ignore", "pipe", "pipe"] },
    );
    return { model: out.trim() };
  } catch (err) {
    const e = err as { stderr?: string; message?: string };
    const reason = (e.stderr ?? e.message ?? "resolve-model failed").trim();
    return { error: reason.replace(/^resolve-model:\s*/, "") };
  }
}

interface FinalMessage {
  text: string;
  usage: unknown;
}

/**
 * Parse a `--mode json` JSONL stream and return the last assistant
 * `message_end`'s concatenated text and usage. Returns null if none found.
 */
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

/** A model-legible error result (no isError field exists on tool results). */
function errorResult(agent: string, reason: string) {
  return {
    content: [{ type: "text" as const, text: `run_agent error (${agent}): ${reason}` }],
    details: { agent, error: true, reason },
  };
}
