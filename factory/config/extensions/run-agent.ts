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
import { createWriteStream, existsSync, lstatSync, readFileSync, unlinkSync } from "node:fs";
import { isAbsolute, join, posix } from "node:path";
import type { Readable } from "node:stream";

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
const ENVELOPE_FIELDS = ["artifact_paths", "disposition", "finding_counts", "next_action"];

/** The only child result content allowed into an orchestrating transcript. */
export interface ChildResultEnvelope {
  disposition: "pass" | "fail" | "block";
  finding_counts: Record<string, number>;
  artifact_paths: string[];
  next_action: string;
}

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
      args.push("--append-system-prompt", persona, "-p", childTask(params.task));

      /**
       * Record the parent repo's HEAD before dispatching, so we can later
       * disclose commits the child made even when its final envelope does not
       * parse (BUG-0008).
       */
      const headBefore = gitLocalHead(cwd);

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

      /**
       * The child may have persisted and committed canonical artifacts before
       * its final message was judged, so any subsequent parse error can still
       * disclose those commits (BUG-0008 / FAGAN-0016).
       */
      if (childResult.cancelled) {
        return cancellationResult(
          params.agent,
          enrichWithChildCommits(cwd, headBefore, {}),
        );
      }

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
          enrichWithChildCommits(cwd, headBefore, { exitCode: childResult.status }),
        );
      }

      const decoded = parseChildResultEnvelope(parsed.text);
      const metadata = {
        model: model || "(pi default)",
        usage: parsed.usage,
        exitCode: childResult.status,
      };
      if (decoded.error) {
        // BUG-0008: the child may have committed canonical artifacts even when
        // its final message does not parse. Disclose any fresh commits the
        // child made between dispatch and return, so a spurious parse error
        // cannot hide completed work.
        const freshCommits = childCommitsSince(cwd, headBefore);
        return errorResult(params.agent, decoded.error, {
          ...metadata,
          ...(freshCommits
            ? {
                freshChildCommits: freshCommits,
                note: "child committed work despite the envelope parse failure — " +
                  "verify the listed commits/artifacts before retrying; do not blindly re-dispatch",
              }
            : {}),
        });
      }
      const artifactError = validateChildResultArtifacts(cwd, decoded.envelope);
      if (artifactError) {
        return errorResult(params.agent, artifactError, metadata);
      }

      return {
        content: [{ type: "text" as const, text: serializeChildResultEnvelope(decoded.envelope) }],
        details: {
          agent: params.agent,
          ...metadata,
        },
      };
    },
  });
}

/** Append the cross-CLI persistence and exact serialization obligation. */
export function childTask(task: string): string {
  return (
    `${task}\n\nBefore returning, persist the complete result in canonical Git-tracked ` +
    "report and finding artifacts. Your final assistant message must be exactly one JSON object " +
    "with only `disposition`, `finding_counts`, `artifact_paths`, and `next_action`, as defined " +
    "by factory/rulebooks/conventions/report-format.md; include no Markdown fence or other prose."
  );
}

/** Decode and structurally validate one exact four-field child envelope. */
export function parseChildResultEnvelope(
  text: string,
): { envelope: ChildResultEnvelope; error?: undefined } | { envelope?: undefined; error: string } {
  const value = extractEnvelopeObject(text);
  if (value === undefined) {
    return { error: "child result envelope invalid: expected one exact JSON object" };
  }
  if (!isRecord(value) || Object.keys(value).sort().join("|") !== ENVELOPE_FIELDS.join("|")) {
    return { error: "child result envelope invalid: expected exactly four canonical fields" };
  }
  if (!(["pass", "fail", "block"] as unknown[]).includes(value.disposition)) {
    return { error: "child result envelope invalid: disposition must be pass, fail, or block" };
  }
  if (!isRecord(value.finding_counts) || Object.keys(value.finding_counts).length === 0) {
    return { error: "child result envelope invalid: finding_counts must name every severity" };
  }
  for (const [severity, count] of Object.entries(value.finding_counts)) {
    if (
      !/^[a-z][a-z0-9_-]*$/.test(severity) ||
      !Number.isInteger(count) ||
      (count as number) < 0
    ) {
      return {
        error: "child result envelope invalid: severity counts must be named non-negative integers",
      };
    }
  }
  if (
    !Array.isArray(value.artifact_paths) ||
    value.artifact_paths.length === 0 ||
    value.artifact_paths.some((path) => typeof path !== "string" || path.length === 0) ||
    new Set(value.artifact_paths).size !== value.artifact_paths.length
  ) {
    return {
      error: "child result envelope invalid: artifact_paths must be a non-empty unique string list",
    };
  }
  if (typeof value.next_action !== "string" || !hasOneToThreeSentences(value.next_action)) {
    return { error: "child result envelope invalid: next_action must contain one to three sentences" };
  }
  return { envelope: value as unknown as ChildResultEnvelope };
}

/** Require every declared result artifact to be a canonical tracked file. */
export function validateChildResultArtifacts(
  cwd: string,
  envelope: ChildResultEnvelope | undefined,
): string | null {
  if (!envelope) return "child result envelope invalid: no envelope to validate";
  for (const path of envelope.artifact_paths) {
    if (
      isAbsolute(path) ||
      path.includes("\\") ||
      posix.normalize(path) !== path ||
      path === "." ||
      path.startsWith("../")
    ) {
      return `child result artifact '${path}' is not a canonical repository-relative path`;
    }
    const absolute = join(cwd, path);
    if (!existsSync(absolute) || !lstatSync(absolute).isFile()) {
      return `child result artifact '${path}' does not exist as a file`;
    }
    try {
      execFileSync("git", ["ls-files", "--error-unmatch", "--", path], {
        cwd,
        stdio: ["ignore", "ignore", "ignore"],
      });
    } catch {
      return `child result artifact '${path}' is not tracked by Git`;
    }
  }
  return null;
}

/** Serialize without retaining any raw child response. */
export function serializeChildResultEnvelope(envelope: ChildResultEnvelope): string {
  return JSON.stringify(envelope);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

/**
 * Locate a JSON object inside a child's final message. The child is told to
 * emit exactly one JSON object, but agents sometimes wrap it in a Markdown
 * fence or leave trailing prose. Recovery tries, in order:
 *  1. the whole trimmed message,
 *  2. each fenced code block,
 *  3. heuristically scanning for balanced `{...}` regions, preferring the
 *     first object with exactly the four canonical envelope fields, then
 *     falling back to the largest by serialized length (FAGAN-0017).
 * Structural validation (exactly four canonical fields) still applies in
 * `parseChildResultEnvelope` — this only finds the object, it does not relax
 * the schema. Returns undefined if no JSON object can be recovered.
 */
export function extractEnvelopeObject(text: string): unknown {
  const candidates: string[] = [];
  const trimmed = text.trim();
  if (trimmed) candidates.push(trimmed);

  // Recover from fenced code blocks: strip the fence markers and any
  // info-string, and treat the enclosed text as candidates.
  const fenceRe = /```(?:[a-zA-Z0-9_-]*)?\s*\n?([\s\S]*?)```/g;
  let m: RegExpExecArray | null;
  while ((m = fenceRe.exec(text)) !== null) {
    if (m[1].trim()) candidates.push(m[1].trim());
  }

  for (const candidate of candidates) {
    try {
      const value = JSON.parse(candidate);
      if (isRecord(value)) return value;
    } catch {
      // try the next candidate
    }
  }

  // Last resort: scan forward from each `{` for a run of balanced braces,
  // parse each well-formed region, and prefer an envelope-shaped object
  // (exactly the four canonical fields); otherwise keep the largest by
  // serialized length (FAGAN-0017).
  const parsed: { value: Record<string, unknown>; str: string }[] = [];
  let start = -1;
  while ((start = text.indexOf("{", start + 1)) !== -1) {
    let depth = 0;
    let inString = false;
    let escaped = false;
    for (let i = start; i < text.length; i++) {
      const ch = text[i];
      if (inString) {
        if (escaped) escaped = false;
        else if (ch === "\\") escaped = true;
        else if (ch === '"') inString = false;
        continue;
      }
      if (ch === '"') {
        inString = true;
        continue;
      }
      if (ch === "{") depth++;
      else if (ch === "}") {
        depth--;
        if (depth === 0) {
          try {
            const value = JSON.parse(text.slice(start, i + 1));
            if (isRecord(value)) {
              parsed.push({ value, str: text.slice(start, i + 1) });
            }
          } catch {
            // keep scanning
          }
          break;
        }
      }
    }
  }
  if (parsed.length === 0) return undefined;

  // Prefer the first envelope-shaped object (exactly four canonical fields)
  const canonicalFields = ENVELOPE_FIELDS.join("|");
  for (const { value } of parsed) {
    if (Object.keys(value).sort().join("|") === canonicalFields) {
      return value;
    }
  }

  // Otherwise, keep the largest by serialized length
  let best = parsed[0];
  for (let i = 1; i < parsed.length; i++) {
    if (parsed[i].str.length > best.str.length) {
      best = parsed[i];
    }
  }
  return best.value;
}

function hasOneToThreeSentences(value: string): boolean {
  const trimmed = value.trim();
  if (!trimmed || !/[.!?]$/.test(trimmed)) return false;
  const sentences = trimmed.split(/(?<=[.!?])\s+/);
  return (
    sentences.length >= 1 &&
    sentences.length <= 3 &&
    sentences.every((sentence) => sentence.trim())
  );
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

/** Current local HEAD SHA of the repo at `cwd`, or null if not a git repo. */
export function gitLocalHead(cwd: string): string | null {
  try {
    const out = execFileSync("git", ["rev-parse", "--short=12", "HEAD"], {
      cwd,
      encoding: "utf-8",
      stdio: ["ignore", "pipe", "ignore"],
    });
    return out.trim() || null;
  } catch {
    return null;
  }
}

/**
 * Commits the child added above `headBefore`, as short-ish lines. Returns null
 * when the repo is absent or no new commits are present. Best-effort only:
 * failures yield null, never a hard error (BUG-0008 disclosure, not a gate).
 */
export function childCommitsSince(cwd: string, headBefore: string | null): string[] | null {
  if (!headBefore) return null;
  try {
    const out = execFileSync(
      "git",
      ["log", "--oneline", "--no-decorate", `${headBefore}..HEAD`],
      { cwd, encoding: "utf-8", stdio: ["ignore", "pipe", "ignore"] },
    );
    const lines = out
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean);
    return lines.length ? lines.slice(0, 10) : null;
  } catch {
    return null;
  }
}

/**
 * Enrich error metadata with child commit disclosure when the child made
 * commits between dispatch and failure (BUG-0008 / FAGAN-0016).
 */
export function enrichWithChildCommits(
  cwd: string,
  headBefore: string | null,
  base: Record<string, unknown>,
): Record<string, unknown> {
  const freshCommits = childCommitsSince(cwd, headBefore);
  if (!freshCommits) return base;
  return {
    ...base,
    freshChildCommits: freshCommits,
    note:
      "child committed work despite the error — " +
      "verify the listed commits/artifacts before retrying; do not blindly re-dispatch",
  };
}

interface FinalMessage {
  text: string;
  usage: unknown;
}

const MAX_JSONL_LINE_BYTES = 4 * 1024 * 1024;
const MAX_STDERR_TAIL_BYTES = 16 * 1024;
const PROGRESS_INTERVAL_BYTES = 1024 * 1024;
const CANCELLATION_GRACE_MS = 250;
const CANCELLATION_DRAIN_MS = 750;

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
  cancelled: boolean;
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
      stdio: ["ignore", "pipe", "pipe"],
      detached: process.platform !== "win32",
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
      cancelled: false,
    };
  }

  let cancelled = false;
  let forceTimer: ReturnType<typeof setTimeout> | undefined;
  let drainTimer: ReturnType<typeof setTimeout> | undefined;
  const cancel = () => {
    if (cancelled) return;
    cancelled = true;
    terminateChild(child, "SIGTERM");
    forceTimer = setTimeout(() => terminateChild(child, "SIGKILL"), CANCELLATION_GRACE_MS);
    drainTimer = setTimeout(() => {
      child.stdout.destroy();
      child.stderr.destroy();
    }, CANCELLATION_DRAIN_MS);
  };
  options.signal?.addEventListener("abort", cancel, { once: true });
  if (options.signal?.aborted) cancel();

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

  const stdoutEnded = waitForPipeSettlement(child.stdout);
  const stderrEnded = waitForPipeSettlement(child.stderr);
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
  let outcome: { status: number | null; error?: string };
  try {
    [outcome] = await Promise.all([outcomePromise, stdoutEnded, stderrEnded]);
    parser.finish();
    if (output && !captureFailed) {
      await new Promise<void>((resolve) => output.end(resolve));
    }
  } finally {
    options.signal?.removeEventListener("abort", cancel);
    if (forceTimer) clearTimeout(forceTimer);
    if (drainTimer) clearTimeout(drainTimer);
    if (cancelled) {
      output?.destroy();
      if (transcript) safeUnlink(transcript);
    }
  }
  if (cancelled) {
    return {
      status: outcome.status,
      finalMessage: parser.last,
      stderrTail: stderrTail.toString("utf-8"),
      bytesRead,
      cancelled: true,
    };
  }
  if (outcome.error) {
    if (transcript) safeUnlink(transcript);
    return {
      ...outcome,
      finalMessage: parser.last,
      stderrTail: stderrTail.toString("utf-8"),
      bytesRead,
      cancelled: false,
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
    cancelled: false,
  };
}

/** Settle exactly once whether a pipe drains, closes, or fails. */
function waitForPipeSettlement(pipe: Readable): Promise<void> {
  if (pipe.readableEnded || pipe.destroyed) return Promise.resolve();
  return new Promise((resolve) => {
    let settled = false;
    const finish = () => {
      if (settled) return;
      settled = true;
      pipe.removeListener("end", finish);
      pipe.removeListener("close", finish);
      pipe.removeListener("error", finish);
      resolve();
    };
    pipe.once("end", finish);
    pipe.once("close", finish);
    pipe.once("error", finish);
  });
}

/** Signal the complete spawned process tree where process groups are available. */
function terminateChild(
  child: ChildProcessWithoutNullStreams,
  signal: NodeJS.Signals,
): void {
  try {
    if (process.platform !== "win32" && child.pid) {
      process.kill(-child.pid, signal);
    } else {
      child.kill(signal);
    }
  } catch {
    // The process may have exited between cancellation and escalation.
  }
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
function errorResult(agent: string, reason: string, metadata: Record<string, unknown> = {}) {
  return {
    content: [{ type: "text" as const, text: `run_agent error (${agent}): ${reason}` }],
    details: { agent, error: true, reason, ...metadata },
  };
}

/** A distinct result for an invocation that spawned successfully but was cancelled. */
function cancellationResult(agent: string, metadata: Record<string, unknown> = {}) {
  const reason = "child process tree terminated because invocation was cancelled; task was not retried";
  return {
    content: [{ type: "text" as const, text: `run_agent cancelled (${agent}): ${reason}` }],
    details: { agent, error: true, cancelled: true, reason, ...metadata },
  };
}
