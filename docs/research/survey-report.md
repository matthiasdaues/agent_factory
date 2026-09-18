# Survey Report — OpenCode CLI Integration into Agent Factory

## 1. Configuration Directory and Files

**Finding**: OpenCode uses `.opencode/` as its project data directory and `opencode.json` (JSONC) as the project config file in the project root. Global config lives at `~/.config/opencode/opencode.json`. Configs merge — later sources override earlier ones on conflict. [SR-0004, SR-0005]

**Factory mapping**: The factory would need a `.opencode/` dot-directory (analogous to `.claude/`, `.github/`, `.pi/`, `.codex/`) and would place its orientation file content so that OpenCode discovers it at session start. The config file (`opencode.json`) would hold agent definitions, MCP servers, permissions, and the `instructions` field pointing to the factory's orientation file.

**Claude Code compatibility**: OpenCode natively reads `.claude/CLAUDE.md` and `.claude/skills/*/SKILL.md` when Claude Code compatibility is enabled (the default). This means a project already wired for Claude Code gets partial factory support in OpenCode out of the box — the orientation file and skills are discovered automatically. [SR-0003]

## 2. System Prompt / Custom Instructions

**Finding**: OpenCode discovers instruction files through two mechanisms \[SR-0003, SR-0012\]:

1. **AGENTS.md** — discovered by walking up from the working directory. If both `AGENTS.md` and `CLAUDE.md` exist in the same directory, only `AGENTS.md` is used.
2. **`instructions` config field** — an array of paths or globs in `opencode.json`, supporting monorepo patterns like `"packages/*/AGENTS.md"`.

The prompt assembly order is: provider header → provider prompt → environment info → custom instructions (AGENTS.md/CLAUDE.md) → agent-specific prompt → user override. [SR-0012]

**Factory mapping**: The factory's orientation file (`factory/config/AGENTS.<cli>.md`) maps directly. For OpenCode, the factory would provide either:

- An `AGENTS.md` in the project root (like Pi and Codex), or
- An `AGENTS.opencode.md` symlinked into `.opencode/` and referenced via the `instructions` config field.

Since OpenCode discovers `CLAUDE.md` when `AGENTS.md` is absent, a project with only Claude Code wiring already gets the factory's orientation file. For a dedicated OpenCode integration, the factory would produce `AGENTS.md` (which takes precedence). [SR-0001, SR-0003]

**Conflict**: Pi and Codex also use `AGENTS.md` in the project root. A project targeting both OpenCode and Pi/Codex would need to reconcile — likely via the `instructions` field in `opencode.json` pointing to a separate file rather than sharing the root `AGENTS.md`.

## 3. Tool Protocol

**Finding**: OpenCode exposes these built-in tools \[SR-0004, SR-0009, SR-0010\]:

| OpenCode Tool | Claude Code Equivalent | Notes                         |
| ------------- | ---------------------- | ----------------------------- |
| `read`        | `Read`                 | File reading                  |
| `write`       | `Write`                | File creation                 |
| `edit`        | `Edit`                 | Diff-based string replacement |
| `grep`        | (Bash `rg`)            | Regex search, uses ripgrep    |
| `glob`        | (Bash `find`)          | File pattern matching         |
| `list`        | (Bash `ls`)            | Directory listing             |
| `bash`        | `Bash`                 | Shell command execution       |
| `task`        | `Agent`                | Subagent dispatch             |
| `skill`       | `Skill`                | Skill invocation              |
| `webfetch`    | `WebFetch`             | URL fetching                  |
| `websearch`   | `WebSearch`            | Web search                    |

MCP support extends the tool set further — local (stdio) and remote (HTTP/SSE) MCP servers can be configured in `opencode.json` under the `mcp` key, with per-agent tool enablement via glob patterns. [SR-0008]
| `lsp` | (not available) | Language server diagnostics |
| `fetch` | `WebFetch` | URL data fetching |
| `sourcegraph` | (not available) | Code search |

The permission system uses the same `allow`/`ask`/`deny` model as Claude Code, with glob-pattern granularity for bash commands. [SR-0009]

**Factory mapping**: The factory's orientation file would need a CLI capabilities section documenting OpenCode's tool names (lowercase, not PascalCase). The dispatch contract's tool-name mapping is straightforward — nearly 1:1 with Claude Code.

## 4. Agent/Skill Definitions

### Agents

**Finding**: OpenCode supports custom agents in two formats \[SR-0002\]:

1. **JSON** — in `opencode.json` under the `agent` key.
2. **Markdown** — files in `.opencode/agents/` (project) or `~/.config/opencode/agents/` (global), with YAML frontmatter (`description`, `mode`, `model`, `temperature`, `steps`, `prompt`, `permission`, `disable`, `color`, `top_p`).

Agent modes: `primary` (user-facing), `subagent` (invoked by other agents), `all` (both).

**Factory mapping**: The factory's markdown agent definitions (`.claude/agents/*.md`) are already in a compatible format. OpenCode's agent frontmatter uses a subset of similar fields. The factory would symlink `factory/agents/` into `.opencode/agents/`. Key differences:

- OpenCode uses `description` (required); factory agents use `description` plus additional frontmatter (`tier`, `eligible_cycles`, `inputs`, `outputs`, `triggers`, `handoff-to`, `version`). OpenCode ignores unknown frontmatter fields, so factory agent files should work as-is — OpenCode would read `description` and the markdown body as the system prompt, ignoring factory-specific fields.
- OpenCode's `mode` field (`primary`/`subagent`/`all`) has no factory equivalent but would default to `subagent` for most factory agents.
- OpenCode's `permission` field in agent frontmatter can restrict tools per-agent.

### Skills

**Finding**: OpenCode natively discovers skills at six paths \[SR-0006\]:

- `.opencode/skills/*/SKILL.md` (project)
- `.claude/skills/*/SKILL.md` (project — Claude Code compat)
- `.agents/skills/*/SKILL.md` (project)
- `~/.config/opencode/skills/*/SKILL.md` (global)
- `~/.claude/skills/*/SKILL.md` (global)
- `~/.agents/skills/*/SKILL.md` (global)

Skills are invoked via the native `skill` tool: `skill({ name: "skill-name" })`.

**Factory mapping**: This is the strongest compatibility point. The factory's skills at `.claude/skills/*/SKILL.md` are already discovered by OpenCode with zero additional wiring. The skill format (`SKILL.md` with YAML frontmatter) is identical. OpenCode's name validation (`^[a-z0-9]+(-[a-z0-9]+)*$`) matches the factory's naming convention.

The factory would not need a separate skill directory for OpenCode — `.claude/skills/` works for both CLIs.

## 5. Subagent Dispatch

**Finding**: OpenCode dispatches subagents via \[SR-0002, SR-0011\]:

- The `task` tool — spawns a child session with a specified subagent.
- `@agent-name` mentions in the prompt.
- Child session navigation (Leader+Down to enter, Right/Left to cycle, Up to return).

Parallel execution is supported — OpenCode is identified as one of six tools that run sub-agents in parallel. However:

- **Worktree isolation is not native.** Subagents get child sessions but share the same working directory. Isolation is advisory (via instructions), not enforced by the runtime. External tools (Superset, opencode-skein) provide worktree management. [SR-0011]
- **`subagent_depth`** defaults to 1 (single-level nesting). Must be configured higher for multi-level dispatch. [SR-0005]
- **Model inheritance is broken** — subagents do not inherit the parent's active model; they fall back to the global `model`. [SR-0011]

**Factory mapping**: OpenCode's dispatch model is closer to Pi than to Claude Code:

| Capability           | Claude Code                       | OpenCode                          |
| -------------------- | --------------------------------- | --------------------------------- |
| Subagent spawn       | `Agent` tool (typed, named, fork) | `task` tool + `@` mentions        |
| Worktree isolation   | Native (`isolation: "worktree"`)  | Not native — advisory or external |
| Parallel fan-out     | Native concurrent dispatch        | Native multi-session              |
| Model per-agent      | Inherited or overridden           | Global fallback (bug)             |
| Session independence | Full (separate context)           | Child sessions (navigable)        |

The factory's dispatch contract can map to OpenCode's `task` tool. The `agent` field maps to the subagent name. However, worktree isolation — critical for the factory's branching policy — would need an extension or external orchestration (like Pi's `dispatch_wave`).

## 6. Session Management

**Finding**: OpenCode persists sessions in SQLite \[SR-0004, SR-0010\]:

- `opencode session list` — list sessions.
- `opencode session delete [sessionID]` — delete session.
- `opencode run [message]` — non-interactive execution.
- `--continue` / `--session [ID]` — continue existing session.
- `--fork` — branch from existing session.
- `--share` — session sharing.
- `opencode export [sessionID]` / `opencode import [file|URL]` — data portability.
- `opencode stats` — usage statistics.
- Auto-compact — summarizes conversations approaching context limits.
- `opencode serve` — headless API mode.

**Factory mapping**: The factory does not depend on session management features. Handoffs are file-based (handoff markdown files). Session persistence is a CLI-internal concern.

## Mapping Table — Factory Integration Points

| Factory Integration Point  | OpenCode Equivalent                                      | Status                              |
| -------------------------- | -------------------------------------------------------- | ----------------------------------- |
| **Dot-directory**          | `.opencode/`                                             | Available                           |
| **Orientation file**       | `AGENTS.md` (root) or `instructions` config field        | Available                           |
| **Claude Code compat**     | Reads `.claude/CLAUDE.md` + `.claude/skills/` by default | Available                           |
| **INDEX.yaml**             | `.opencode/INDEX.yaml` (symlink)                         | Needs wiring (custom, not native)   |
| **Agent format**           | Markdown `.md` with YAML frontmatter                     | Compatible (ignores unknown fields) |
| **Agent location**         | `.opencode/agents/`                                      | Available                           |
| **Skill format**           | `SKILL.md` with YAML frontmatter                         | Identical                           |
| **Skill location**         | `.opencode/skills/` or `.claude/skills/` (compat)        | Available (zero-config via compat)  |
| **Skill invocation**       | Native `skill` tool                                      | Available                           |
| **Subagent dispatch**      | `task` tool + `@` mentions                               | Available                           |
| **Parallel fan-out**       | Native multi-session                                     | Available                           |
| **Worktree isolation**     | Not native — advisory or external                        | **Gap**                             |
| **Hooks (PreToolUse)**     | Not available (open issue #12472)                        | **Blocker**                         |
| **Hooks (Stop)**           | Not available                                            | **Blocker**                         |
| **Step guards**            | Not available (depends on hooks)                         | **Blocker**                         |
| **Git safety hooks**       | Not available (depends on hooks)                         | **Blocker**                         |
| **Freshness check hooks**  | Not available (depends on hooks)                         | **Blocker**                         |
| **Model matrix**           | `provider/model` format in `opencode.json`               | Available (different ID format)     |
| **MCP support**            | Local (stdio) + remote (HTTP/SSE)                        | Available                           |
| **Per-agent MCP tools**    | Glob-pattern enable/disable                              | Available                           |
| **Task tracking**          | No equivalent to `TaskCreate`/`TaskUpdate`               | **Gap**                             |
| **Workflow orchestration** | No equivalent to `Workflow` tool                         | **Gap**                             |
| **Persistent memory**      | No equivalent to file-based memory system                | **Gap**                             |
| **Permission model**       | `allow`/`ask`/`deny` with glob patterns                  | Available                           |

## Gaps and Blockers

### Blockers (prevent full integration)

1. **No hooks support** — The factory's guardrail system (git safety, step guards, freshness checks) relies on PreToolUse hooks in `.claude/settings.json`. OpenCode does not read or execute these hooks. GitHub issue #12472 requests this but is unresolved. Without hooks, the factory cannot enforce its safety invariants in OpenCode sessions. [SR-0007]

2. **No Stop hook re-activation** — Claude Code's Stop hook can inject feedback and resume the agent (exit code 2). OpenCode's `session.idle` is fire-and-forget. This prevents the factory's workflow completion validation. [SR-0007]

### Gaps (workable but require adaptation)

3. **No native worktree isolation** — Subagents share the working directory. The factory's branching policy requires worktree-isolated agents for parallel implementation. This could be addressed by an OpenCode plugin/extension or by external orchestration (like opencode-skein), similar to how Pi uses `dispatch_wave`. [SR-0011]

4. **No TaskCreate/TaskUpdate** — OpenCode has no built-in task-tracking tool. The factory uses these for progress tracking. Could be provided via an MCP server or ignored (task tracking is a convenience, not a safety invariant).

5. **No Workflow tool** — Multi-agent workflow orchestration would need external tooling or an MCP server.

6. **No persistent memory** — OpenCode has no cross-session memory system. Could be provided via an MCP server or file-based convention.

7. **Model inheritance bug** — Subagents fall back to global model instead of inheriting parent's model. This affects the factory's model matrix per-agent tier system. [SR-0011]

8. **AGENTS.md collision** — Pi and Codex also use `AGENTS.md` in the project root. Co-existence would require OpenCode to use the `instructions` config field instead.

## Uncertainties and Evidence Gaps

- **Plugin API**: OpenCode's `plugin` config key accepts an array, but the plugin authoring format is not documented in the sources examined. A custom plugin might be able to provide hooks, task tracking, or worktree isolation.
- **Experimental features**: `OPENCODE_EXPERIMENTAL*` environment variables may enable workspace support and background subagents, but these are undocumented.
- **`compatibility` frontmatter field**: The skill system accepts a `compatibility` field but its values are not documented — it might gate skill availability by CLI.
- **`instructions` field interaction**: Whether the `instructions` config field merges with or replaces auto-discovered AGENTS.md files is not confirmed.

## Candidates for Deeper Study

1. **OpenCode plugin API** — Could a plugin provide PreToolUse/PostToolUse hooks, task tracking, and worktree isolation? This is the critical path for full integration.
2. **opencode-skein** — An external worktree orchestrator for OpenCode. Could it serve the same role as Pi's `dispatch_wave`?
3. **OpenCode experimental workspace support** — If workspaces provide isolation, this could address the worktree gap.
4. **MCP-based factory extensions** — Could an MCP server provide task tracking, memory, and workflow orchestration to OpenCode?
