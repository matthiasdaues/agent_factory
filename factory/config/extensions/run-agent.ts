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
import { execFileSync, spawn } from "node:child_process";
import type { ChildProcessWithoutNullStreams } from "node:child_process";
import { createWriteStream, existsSync, readFileSync, unlinkSync } from "node:fs";
import { join } from "node:path";

import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";
import { Type } from "typebox";
import {
  activeSessionId,
  activeUsageRoot,
  capturePiFile,
  createPiCaptureFile,
  INLINE_CAPTURE_ENV,
  newSessionId,
  SESSION_ENV,
  USAGE_ROOT_ENV,
} from "./pi-usage.ts";

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
    async execute(_toolCallId, params, signal, onUpdate, ctx) {
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
      const usageRoot = activeUsageRoot(cwd);
      const parentSessionId = activeSessionId(
        (ctx as { sessionManager?: { getSessionFile(): string | undefined } }).sessionManager,
      );
      const childResult = await runPiStreamed({
        args,
        cwd,
        signal,
        onUpdate,
        transcript: createPiCaptureFile(cwd, childSessionId),
        env: {
          ...process.env,
          [DEPTH_ENV]: String(depth + 1),
          [SESSION_ENV]: childSessionId,
          PI_AGENT_FACTORY_PARENT_SESSION_ID: parentSessionId || "",
          [INLINE_CAPTURE_ENV]: "1",
          [USAGE_ROOT_ENV]: usageRoot,
        },
      });

      if (childResult.transcript) capturePiFile(cwd, childResult.transcript, {
        sessionId: childSessionId,
        parentSessionId,
        depth: depth + 1,
        agent: params.agent,
        model: model || undefined,
        exitStatus: childResult.status === 0 ? "success" : "failure",
      });

      if (childResult.error) {
        return errorResult(params.agent, `failed to spawn pi: ${childResult.error}`);
      }

      const parsed = childResult.finalMessage;
      if (childResult.status !== 0 || !parsed) {
        return errorResult(
          params.agent,
          `child pi exited ${childResult.status} without a usable message_end.\n` +
            `stdout bytes: ${childResult.bytesRead}.\n` +
            `stderr tail:\n${childResult.stderrTail}`,
        );
      }

      return {
        content: [{ type: "text" as const, text: parsed.text }],
        details: {
          agent: params.agent,
          model: model || "(pi default)",
          usage: parsed.usage,
          exitCode: childResult.status,
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

const MAX_JSONL_LINE_BYTES = 4 * 1024 * 1024;
const MAX_STDERR_TAIL_BYTES = 16 * 1024;
const PROGRESS_INTERVAL_BYTES = 1024 * 1024;

interface RunPiOptions {
  args: string[];
  cwd: string;
  env: NodeJS.ProcessEnv;
  signal?: AbortSignal;
  transcript?: string;
  onUpdate?: (update: ProgressUpdate) => void;
}

interface ProgressUpdate {
  content: Array<{ type: "text"; text: string }>;
  details: Record<string, unknown>;
}

interface RunPiResult {
  status: number | null;
  error?: string;
  finalMessage: FinalMessage | null;
  stderrTail: string;
  transcript?: string;
  bytesRead: number;
}

/** Run one Pi child while retaining only bounded diagnostic and parser state. */
async function runPiStreamed(options: RunPiOptions): Promise<RunPiResult> {
  const parser = new JsonlFinalMessageParser();
  let stderrTail = Buffer.alloc(0);
  let bytesRead = 0;
  let nextProgress = PROGRESS_INTERVAL_BYTES;
  const transcript = options.transcript;
  const output = transcript ? createWriteStream(transcript, { flags: "a", mode: 0o600 }) : null;
  let captureFailed = false;
  output?.on("error", () => {
    captureFailed = true;
    if (transcript) safeUnlink(transcript);
  });
  let child: ChildProcessWithoutNullStreams;
  try {
    child = spawn("pi", options.args, {
      cwd: options.cwd,
      env: options.env,
      signal: options.signal,
      stdio: ["ignore", "pipe", "pipe"],
    });
  } catch (error) {
    output?.destroy();
    if (transcript) safeUnlink(transcript);
    return {
      status: null,
      error: error instanceof Error ? error.message : String(error),
      finalMessage: null,
      stderrTail: "",
      bytesRead,
    };
  }

  child.stdout.on("data", (chunk: Buffer) => {
    bytesRead += chunk.length;
    parser.push(chunk);
    if (output && !captureFailed && !output.write(chunk)) {
      child.stdout.pause();
      const resume = () => child.stdout.resume();
      output.once("drain", resume);
      output.once("error", resume);
    }
    if (bytesRead >= nextProgress) {
      nextProgress = bytesRead + PROGRESS_INTERVAL_BYTES;
      options.onUpdate?.({
        content: [{ type: "text", text: `run_agent streaming (${formatMiB(bytesRead)} MiB)` }],
        details: { bytesRead },
      });
    }
  });
  child.stderr.on("data", (chunk: Buffer) => {
    stderrTail =
      chunk.length >= MAX_STDERR_TAIL_BYTES
        ? chunk.subarray(chunk.length - MAX_STDERR_TAIL_BYTES)
        : Buffer.concat([stderrTail, chunk]).subarray(-MAX_STDERR_TAIL_BYTES);
  });

  const stdoutEnded = new Promise<void>((resolve) => child.stdout.once("end", resolve));
  const stderrEnded = new Promise<void>((resolve) => child.stderr.once("end", resolve));
  const outcomePromise = new Promise<{ status: number | null; error?: string }>((resolve) => {
    let settled = false;
    const finish = (value: { status: number | null; error?: string }) => {
      if (settled) return;
      settled = true;
      resolve(value);
    };
    child.once("error", (error) => finish({ status: null, error: error.message }));
    child.once("close", (code) => finish({ status: code }));
  });
  const [outcome] = await Promise.all([outcomePromise, stdoutEnded, stderrEnded]);
  parser.finish();
  if (output && !captureFailed) {
    await new Promise<void>((resolve) => output.end(resolve));
  }
  if (outcome.error) {
    if (transcript) safeUnlink(transcript);
    return {
      ...outcome,
      finalMessage: parser.last,
      stderrTail: stderrTail.toString("utf-8"),
      bytesRead,
    };
  }
  options.onUpdate?.({
    content: [{ type: "text", text: `run_agent child exited (${formatMiB(bytesRead)} MiB)` }],
    details: { bytesRead, exitCode: outcome.status },
  });
  return {
    ...outcome,
    finalMessage: parser.last,
    stderrTail: stderrTail.toString("utf-8"),
    transcript: captureFailed ? undefined : transcript,
    bytesRead,
  };
}

/** Incrementally decode JSONL across arbitrary byte chunk boundaries. */
class JsonlFinalMessageParser {
  private pending = Buffer.alloc(0);
  private discardingOversizedLine = false;
  last: FinalMessage | null = null;

  push(chunk: Buffer): void {
    let remaining = chunk;
    while (remaining.length > 0) {
      if (this.discardingOversizedLine) {
        const newline = remaining.indexOf(0x0a);
        if (newline < 0) return;
        this.discardingOversizedLine = false;
        remaining = remaining.subarray(newline + 1);
        continue;
      }

      const newline = remaining.indexOf(0x0a);
      const fragment = newline < 0 ? remaining : remaining.subarray(0, newline);
      this.pending = Buffer.concat([this.pending, fragment]);
      if (this.pending.length > MAX_JSONL_LINE_BYTES) {
        this.pending = Buffer.alloc(0);
        this.discardingOversizedLine = newline < 0;
      } else if (newline >= 0) {
        this.consumeLine();
      }
      if (newline < 0) return;
      remaining = remaining.subarray(newline + 1);
    }
  }

  finish(): void {
    if (!this.discardingOversizedLine) this.consumeLine();
  }

  private consumeLine(): void {
    const parsed = parseFinalMessage(this.pending.toString("utf8"));
    if (parsed) this.last = parsed;
    this.pending = Buffer.alloc(0);
  }
}

function safeUnlink(path: string): void {
  try {
    unlinkSync(path);
  } catch {
    // Best-effort staging cleanup must not mask the child result.
  }
}

function formatMiB(bytes: number): string {
  return (bytes / (1024 * 1024)).toFixed(1);
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
