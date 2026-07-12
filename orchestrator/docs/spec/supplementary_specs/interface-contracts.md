# Interface Contracts — Agent Session Orchestrator

DTOs and schemas at the system's boundaries. Applying **Dependency Inversion** (the core depends on these abstractions, not concretions) and **Interface Segregation** (each contract is minimal).

> **Scope note (amended 2026-07-12, PhaseRunner collapse):** the *CLI Adapter*, *Invocation Log*, and *Invocation Context & Prompt Composer* sections below describe ports and DTOs deleted from the orchestrator — `CLIAdapter`, the invocation-log writer, `InvocationContext`, and `PromptComposer` all moved to `factory/`. Kept for history; the orchestrator no longer implements them. See the repo-root `docs/spec/prd.md` and `docs/adr/0002-factory-owns-flow-control-orchestrator-is-a-trigger.md`. The *Gate Verification*, *Finding*, *Story*, *model.conf*, *Run State*, *Run Lock*, *Configuration Store*, *Adapter Registry*, *Settings Resolver*, *Menu Renderer*, and *Agent Tier Extension* sections remain accurate.

## CLI Adapter

_(Superseded — moved to factory.)_

The seam that makes the orchestrator CLI-agnostic. Concrete adapters (Copilot first; Claude, Gemini later) implement this one method.

```
InvocationResult:
    exit_code:    int
    stdout:       str
    stderr:       str
    timed_out:    bool
    auth_error:   bool      # auth/availability failure (halt, BR-018)
    config_error: bool      # operator-fixable, deterministically-repeating failure (halt, BR-020)

CLIAdapter.invoke(prompt: str, cwd: Path, timeout_s: int, model: str | None = None) -> InvocationResult
```

- The core passes a fully composed prompt, a working directory, and optionally a resolved model; the adapter owns all CLI-specific flags for non-interactive invocation. When `model` is provided, the adapter uses it for this invocation, overriding any constructor default.
- The adapter must not leak CLI-specific types back to the core — only `InvocationResult`.
- `auth_error` lets the core distinguish an author failure (loop) from an adapter failure (halt, BR-018).
- `config_error` lets the core halt on an operator-fixable failure that would fail identically on every retry — a bad `--model` id, an unknown flag (BR-020, ATAM-R01/T-11). Without it, such an error loops the author for the full cap, burning CLI credits, then halts with a misleading "cap exhausted" reason. `auth_error` takes precedence when both could match. Everything else non-zero is an author failure (loop).
- **Adapter obligation (isolation, ATAM-R11/T-18)**: each adapter must force a clean session — it must never pass a resume/continue flag (`--continue`, `--resume`) — so a fresh process cannot silently inherit a persisted session. Adapter tests assert this.

## Gate Verification

The orchestrator no longer stages, commits, or runs pre-commit hooks itself. Agents commit their own work; pre-commit hooks fire inside the agent subprocess. The orchestrator's gate is a **working-tree cleanliness check** after the agent exits.

_(Amended)_ The table below described `WorkingTreeGate.verify()` as a per-iteration step inside the deleted phase loop. The method and `GateResult` DTO are unchanged and still real, but the orchestrator now calls `verify()` from exactly one place — `ApprovalService.approve()`'s artifact-staleness re-gate (VR-012) — not from a phase loop. The `→ AwaitingApproval or Reviewing` / `→ Halted` / `→ RetryOrHalt` transitions below are factory's, driven by the same `GateResult` shape.

```
WorkingTreeGate.verify(cwd: Path, exit_code: int) -> GateResult
```

| Agent exit code | Working tree | `GateResult`                                       | Action                           |
| --------------- | ------------ | -------------------------------------------------- | -------------------------------- |
| 0               | clean        | `passed=true`                                      | → AwaitingApproval or Reviewing  |
| 0               | dirty        | `passed=false, errored=true, hook="confabulation"` | → Halted (trust violation)       |
| non-zero        | dirty        | `passed=false, errored=false`                      | → RetryOrHalt (clean tree first) |
| non-zero        | clean        | `passed=false, errored=false`                      | → RetryOrHalt                    |

```
GateResult:
    passed:      bool      # working tree clean after agent exit
    errored:     bool      # confabulation (exit 0 + dirty) — halt, not loopable
    hook:        str       # "working-tree" or "confabulation"
    error_count: int       # count of dirty files (0 when passed)
    timed_out:   bool      # reserved (always false for working-tree checks)
    output:      str       # list of dirty files (transient — not persisted)
```

- On RetryOrHalt with a dirty tree, the orchestrator cleans the working tree (`git checkout`/`git clean`) before re-invoking the agent, preserving session isolation (ADR-0002).
- Committed work on the run branch survives the clean. Only uncommitted changes are lost.
- The run branch is created/ensured by the orchestrator before invocation. Agents commit on the run branch.

## Invocation Log (append-only)

_(Superseded — moved to factory. No orchestrator component writes `.orchestrator/log.jsonl` any longer; the read-only `InvocationLogReader` port remains but has no concrete adapter, so `status > log` always renders empty.)_

Per-invocation observability (FR-J, QS-13, ATAM-R06/T-16). Each agent invocation appends one JSON line to `.orchestrator/log.jsonl` after it completes, matching the `AGENT_INVOCATION` entity: `agent`, `role`, `adapter`, `model`, `exit_code`, `duration_ms`, `timed_out`, `auth_error`, `config_error`, plus the resulting `gate` outcome where one followed (`passed`, `errored`, `hook`, `error_count`, `gate_timed_out`). The core writes it through a `Logger` port so the sink stays swappable; the append-only file is the default adapter. Reads never drive control flow (logs are for the operator, not the loop).

## Invocation Context & Prompt Composer

_(Superseded — moved to factory. `InvocationContext` and `PromptComposer` are deleted from the orchestrator.)_

The `InvocationContext` carried the workstep identity from the phase runner to the prompt composer (FR-L).

```
InvocationContext:
    phase:     str        # "requirements", "architecture", "planning", "implementation"
    role:      AgentRole  # AUTHOR or REVIEWER
    iteration: int        # 0-based iteration count within the phase
```

The `PromptComposer` assembles the full prompt passed to the CLI adapter. The `InvocationContext` is **required** — every orchestrator invocation must provide context.

```
PromptComposer.compose(
    agent_info: AgentInfo,
    context_paths: list[Path],
    invocation: InvocationContext,
    findings: list[Finding] | None = None,
    skill: str | None = None,
) -> str
```

`skill` (ST-0052, UC-11) scopes a `run-step` invocation to one of the agent's declared skills instead of its full workflow. It is a prompt-composition-only concern (BR-051): the `# Agent Definition` section is never rewritten, only the `# Call to Action` template selection changes. `None` (the default) or the `"all skills"` sentinel selects the standard full-workflow templates below (BR-052); the caller (`orchestrate run-step --skill`) is responsible for validating the requested skill against `AgentInfo.skills` before calling `compose` (VR-038) — `compose` itself does not validate.

Prompt section order: `# Agent Definition` → `# Project Context` → `# Findings from Prior Iteration` (if any) → `# Call to Action`.

Six call-to-action templates. When `skill` is set, it takes priority over `role`/`iteration`; otherwise selection is by `role` and `iteration` as before:

| Condition                         | Template                                                                                                                                              |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| Author, iteration 0               | `"Begin the {phase} phase. Execute the workflow defined in your Agent Definition above, starting at Step 1."`                                         |
| Author, iteration 1+              | `"This is iteration {n} of the {phase} phase. Address the findings listed above, then re-execute your workflow."`                                     |
| Reviewer, iteration 0             | `"Review the {phase} artifacts. Follow the review workflow in your Agent Definition. File findings per the specified format."`                        |
| Reviewer, iteration 1+            | `"This is iteration {n} of the {phase} review. The author has addressed prior findings. Re-review the artifacts and file any remaining issues."`      |
| Standalone (`run-step`)           | `"Execute the workflow defined in your Agent Definition above."`                                                                                      |
| Skill-scoped (`run-step --skill`) | `'Execute only the "{skill}" skill's workflow step, as defined in your Agent Definition above. Do not execute the full workflow or any other skill.'` |

## Finding (store DTO)

One JSON file per finding under `findings/`. IDs are assigned by the orchestrator on ingest (BR-019); the pattern allows unbounded growth. Validated on write (VR-006, VR-007). This store is the review loop's single source of truth for loop state; `docs/findings/*.md` is the ingestion input it is projected from, not a second store ([ADR-0019](../../adr/0019-findings-store-remains-the-loop-source-of-truth.md)).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Finding",
  "type": "object",
  "required": ["id", "phase", "iteration", "source", "code", "severity", "artifact", "message", "status"],
  "additionalProperties": false,
  "properties": {
    "id":          { "type": "string", "pattern": "^FND-[0-9]{4,}$" },
    "phase":       { "type": "string" },
    "iteration":   { "type": "integer", "minimum": 1 },
    "source":      { "enum": ["spec-lint", "semantic"] },
    "code":        { "type": "string" },
    "severity":    { "enum": ["error", "warning", "info"] },
    "artifact":    { "type": "string" },
    "message":     { "type": "string" },
    "status":      { "enum": ["open", "superseded", "resolved"] },
    "created_by":  { "type": "string" },
    "resolved_by": { "type": ["string", "null"] }
  }
}
```

- **Ingest mapping** _(superseded — moved to factory; `FindingIngestor` is deleted from the orchestrator)_: the deterministic pass runs `spec-lint --format json`; the semantic pass's findings are read from the review agent's filed `docs/findings/*.md` — every file whose frontmatter `status` is `open` (decision in [ADR-0012](../../adr/0012-ingest-findings-from-filed-markdown.md), superseding the stdout-block mechanism of [ADR-0011](../../adr/0011-reviewer-findings-ingest-contract.md)). A `FindingIngestor` port exposed two methods: `ingest_open_findings(phase, iteration)` read filed markdown findings, and `ingest_gate_output(gate_output, phase, iteration)` parsed deterministic gate/spec-lint findings from pre-commit stdout (FAGAN-0034). Gate-output parsing tolerated mixed stdout (hook banner text around an embedded JSON findings block) and de-duplicated findings by content — code, severity, artifact, message — so a finding echoed both as a bare object and inside a `findings` array, or repeated across two output blocks, was counted once (FAGAN-0045). The store still stamps `id` (monotonic allocator via `FindingsStore.next_id()`), `phase`, and `iteration` on write; the orchestrator's `FilesystemFindingsStore` retains this allocator even though nothing in the orchestrator calls it today. Neither source mints its own ID. `next_id()` returns the next available `FND-NNNN` identifier, monotonically increasing across the store.
- **Severity mapping**: sources report on their own scale — `spec-lint` already emits `error | warning | info`; the semantic reviewer uses the review scales (`critical | major | minor`, or `high | medium | low` for the security and ATAM reviews). The ingestor maps every scale onto this DTO's `error | warning | info` (`critical`/`major`/`high` → `error`; `medium`/`minor` → `warning`; `low` → `info`) so no reviewer finding is dropped for an unrecognized label. Severity casing is lowercase everywhere (BR-002).
- **Iteration (cycle) tagging**: a finding's `iteration` is the 1-based cycle that must address it, which is `RunState.iteration + 1` (the run counter is 0-based, minimum 0; a finding's is minimum 1). A reviewer running after the pass at run-iteration *N* tags its findings *N+1*; the loop counts the open findings of that just-produced cycle (SF-04), and after the loop-back increment the author reads them via the store at its new iteration.
- **Persisted review cycle (FAGAN-0040)**: the reviewer records the cycle it just tagged in `PhaseRecord.last_reviewed_cycle`, and `ApprovalService.approve()` and the `status` projection count open findings on *that* stored cycle rather than re-deriving `iteration + 1`. Re-deriving is wrong on the empty-commit pause path, which returns to `awaiting-approval` without ingesting or advancing the iteration, leaving `iteration + 1` pointing past the still-open findings. `null` means no review has run for the phase (a gate-only phase); approval then has nothing to block on.
- **Lifecycle**: `open` → `superseded` (a newer iteration replaced it, BR-014) or `resolved` (a human closed it, T-05). The loop-exit condition (SF-04) counts only `open` findings of the **latest** iteration.

## Story (backlog item)

One markdown file per story under `backlog/`, named by id (`ST-NNNN.md`). The file is strict **YAML frontmatter** (the machine fields below, JSON-schema validated by `backlog-lint`) followed by a prose body (the human story: narrative, INVEST, acceptance criteria). No machine field is restated in the body; the orchestrator reads only the frontmatter (FR-K, T-10). The prose is human- and implementation-agent-facing.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StoryFrontmatter",
  "type": "object",
  "required": ["id", "epic", "title", "tier", "status", "outputs"],
  "additionalProperties": false,
  "properties": {
    "id":             { "type": "string", "pattern": "^ST-[0-9]{4,}$" },
    "epic":           { "type": "string" },
    "title":          { "type": "string" },
    "tier":           { "enum": ["economy", "standard", "strong"] },
    "status":         { "enum": ["pending", "in-progress", "done", "blocked"] },
    "deps":           { "type": "array", "items": { "type": "string", "pattern": "^ST-[0-9]{4,}$" } },
    "traces":         { "type": "array", "items": { "type": "string" } },
    "outputs":        { "type": "array", "items": { "type": "string" } }
  }
}
```

- `tier` drives model selection (FR-K1) — the same field name and enum as agent frontmatter's `tier`, looked up directly in `model.conf`. `traces` carries the use-case/requirement ids the story realizes, so `backlog-lint` can check traceability. `outputs` are the story's declared artifact paths, giving the implementation phase its BR-016 staging and FR-H1 completion, exactly as an agent's `outputs` do for the earlier phases.

## model.conf

The operator-curated tier router (FR-K2, FR-K5, ADR-0020, ADR-0021): `[facts]` maps each tier to a concrete model, per configured CLI. No policy layer — a tier is either configured for a CLI or it isn't. Validated by `matrix-lint`: well-formed `<cli>.<tier>` keys, a valid `on_missing`, and a coverage warning for any CLI missing a tier.

> **Authority note (T-32, SPEC-0010, ADR-0021):** `model.conf` is read directly by `ModelResolver` at resolution time — no separate runtime dictionary sits between the file and a resolved model. `AdapterRegistry`'s per-adapter `ModelDictionary` (`.orchestrator/config.toml`) remains a local, discoverable cache used for menu-mode display and `configure > cli > {adapter}` management, populated from `model.conf` on a gap-fill basis (an existing local entry is never overwritten by import) — but it is not in the resolution path.

```
[facts]
  <cli>.economy  = <model id>       # e.g. copilot.economy = ...
  <cli>.standard = <model id>
  <cli>.strong   = <model id>       # e.g. claude.strong = claude-opus-4-8
  on_missing     = halt | auto      # default halt (FR-K4, BR-020)
```

- `model.conf` keeps the backlog CLI-agnostic (a story stores only its tier, never a concrete model id) and is the only tier→model source that works without an orchestrator process running (the `factory/` playbook workflow reads it directly).

## Run State (`.orchestrator/run.json`)

The resumable record of a run. Written atomically (BR-017). Validated on write (VR-010). `idle` is **not** a persisted mode — an absent `run.json` *is* idle (UC-05).

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RunState",
  "type": "object",
  "required": ["run_id", "branch", "chain", "current_phase", "iteration", "mode", "phases"],
  "additionalProperties": false,
  "properties": {
    "run_id":        { "type": "string" },
    "branch":        { "type": "string" },
    "chain":         { "type": "array", "items": { "type": "string" } },
    "current_phase": { "type": "string" },
    "iteration":     { "type": "integer", "minimum": 0 },
    "mode":          { "enum": ["running", "paused", "halted", "complete"] },
    "tooling_version": { "type": ["string", "null"] },
    "phases": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "author", "status"],
        "additionalProperties": false,
        "properties": {
          "name":      { "type": "string" },
          "author":    { "type": "string" },
          "reviewer":  { "type": ["string", "null"] },
          "status":    { "enum": ["pending", "authoring", "gating", "reviewing", "awaiting-approval", "complete", "halted"] },
          "iteration": { "type": "integer", "minimum": 0 },
          "last_reviewed_cycle": { "type": ["integer", "null"], "minimum": 0 },
          "halted_from": { "type": ["string", "null"], "enum": ["authoring", "gating", "reviewing", null] },
          "last_gate": {
            "type": ["object", "null"],
            "additionalProperties": false,
            "properties": {
              "passed":      { "type": "boolean" },
              "errored":     { "type": "boolean" },
              "hook":        { "type": "string" },
              "error_count": { "type": "integer", "minimum": 0 },
              "timed_out":   { "type": "boolean" }
            }
          },
          "rejection_note": { "type": ["string", "null"] }
        }
      }
    }
  }
}
```

- `branch` records the dedicated run branch (BR-016).
- Each phase names its `author` and optional `reviewer` (BR-006) — a `null` reviewer is a gate-only phase.
- `mode: paused` is the persisted awaiting-approval state (BR-003, S-03).
- `last_gate` records the most recent `GateResult` for the phase (null before the first gate), so `status` can report it without re-running the gate (FR-A4, ATAM-R05/T-15).
- **Resume idempotency (ATAM-R07/T-17)**: `status` plus the run branch's HEAD are the sub-phase checkpoint. On resume the orchestrator does not blindly redo the current iteration: if the current iteration's artifact commit already exists on the run branch it skips re-committing (avoiding a spurious empty-commit no-progress iteration), and if the reviewer already ingested findings for the current iteration it skips re-invoking the reviewer (avoiding duplicate semantic findings). See [state-machines](state-machines.md) and UC-06.

## Run Lock

A single active run is enforced by a lock (BR-017). The orchestrator refuses to start if a lock is held or `run.json` shows `mode: running`; `resume` reclaims the lock for the recorded run.

- **Liveness (ATAM-R09)**: the lock records the holder's PID and start time. On start, a lock whose PID is no longer alive is treated as stale and reclaimable with a warning, so a crashed run does not wedge the tool; a live PID still blocks (BR-017).

## Configuration Store

```
ConfigStore (port):
  load() -> Config | None
  save(config: Config) -> None  # atomic write
  
Config:
  adapter: str | None
  timeout: int | None
  cap: int | None
  auto_approve: bool | None
```

- `None` fields mean the operator has not set an override, so the resolver falls through to the next precedence layer.
- The store is persisted as `.orchestrator/config.toml`.
- `save()` writes atomically: write to a temporary file in the target directory, then rename into place.

## Adapter Registry

```
AdapterRegistry (port):
  list_adapters() -> list[AdapterEntry]
  get_adapter(name: str) -> AdapterEntry
  register(name: str, binary_path: str) -> None
  unregister(name: str) -> None  # removes adapter + model dictionary
  
AdapterEntry:
  name: str
  binary_path: str
  
ModelDictionary:
  get_model(tier: str) -> str | None
  set_model(tier: str, model_id: str) -> None
  remove_model(tier: str) -> None
  list_models() -> list[tuple[str, str]]  # (tier, model_id)
```

- The registry and its model dictionaries persist in `.orchestrator/config.toml`, the same store as `Config` (ADR-0017, resolves SPEC-0010) — local, machine-specific, git-ignored.
- Each adapter owns one model dictionary keyed by the fixed tier vocabulary, used for menu-mode display and `configure > cli > {adapter}` management — not the resolution path (see `model.conf`'s Authority note above, ADR-0021).
- `unregister()` removes the adapter record and its dictionary entries as one logical operation.

## Settings Resolver

```
SettingsResolver:
  resolve(key: str, menu_value: T | None, cli_flag: T | None) -> T
```

Precedence: `menu_value > cli_flag > config_store.load()[key] > BUILT_IN_DEFAULTS[key]`.

- A missing or `None` value at any layer means "continue to the next layer," not "stop with null."
- The resolver centralizes precedence so menu mode and direct CLI mode produce the same effective settings.

## Menu Renderer (port)

```
MenuRenderer (port):
  render_menu(items: list[MenuItem], selected_index: int) -> None
  render_display(content: str) -> None
  get_keypress() -> KeyEvent
  
MenuItem:
  label: str
  suffix: str | None  # e.g. "[strong]" tier tag
  is_default: bool     # ★ marker
  
KeyEvent: enum(UP, DOWN, ENTER, BACK, EXIT)
```

- The renderer abstracts the concrete terminal library from the application layer.
- `render_menu()` owns cursor presentation; `render_display()` owns read-only screens such as agent detail or backlog summaries.
- `get_keypress()` returns normalized navigation events rather than raw terminal bytes.

## Agent Tier Extension

```
AgentInfo (extended):
  name: str
  outputs: list[str]
  definition_path: Path
  skills: list[str]
  tier: str | None      # "economy" | "standard" | "strong"
  interactive: bool      # default interactive policy
```

The agent registry shall parse `tier` and `interactive` from agent YAML frontmatter.

- **Null-tier fallback (FR-R11, SPEC-0006):** When `AgentInfo.tier` is `None` (the agent definition omits a `tier` key), the model resolution chain shall treat the agent as `standard` tier. This ensures every agent can resolve a model even before all agent definitions carry explicit tier declarations.
