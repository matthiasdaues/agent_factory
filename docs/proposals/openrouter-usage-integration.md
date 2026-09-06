---
schema_version: 2
title: "OpenRouter Usage Integration"
status: draft
owner: matthias
created: 2026-08-07
updated: 2026-08-07
supersedes:

impact:
  scope: cross_component
  architecture_change: false
  external_contract_change: true
  boundaries:
    - factory/config/extensions/openrouter-session.ts
    - factory/config/extensions/pi-usage.ts
    - factory/scripts/openrouter-provision
    - factory/scripts/openrouter-usage
    - factory/scripts/init-factory
    - factory/scripts/remove-factory

governance:
  assurance: elevated
  risk_domains:
    - compatibility
    - data_integrity
    - operations
    - security

estimate:
  as_of: 2026-08-07
  basis: judgment
  confidence: low
  human_review_hours: unknown
  normalized_tokens: unknown
---

# Feature Request: OpenRouter Usage Integration

## Summary

Bridge the factory's local usage-capture records to OpenRouter's server-side
accounting. The release adds two capabilities in three phases: session-level
request grouping visible in OpenRouter's logs (Phase 1), per-project API key
provisioning with budget controls (Phase 2), and a query tool for server-side
cost data (Phase 3, deferred). A prerequisite verification phase (Phase 0)
confirms two untested assumptions about Pi's extension and authentication
behaviour before any production code is written.

The one question this feature answers that the factory cannot answer today:
*what did this project actually cost on OpenRouter, and how does a specific
agent run look in the provider's own accounting?*

## Motivation

The factory already captures runtime token usage locally: `usage-capture`
normalises each CLI's transcript through `cl100k_base` and appends one JSONL
record per agent invocation. Provider-reported numbers are kept alongside for
cost reconciliation. This system is implemented and shipping.

OpenRouter independently tracks every API call it routes — with the model's
native tokenizer, actual dollar cost, cache hit rates, provider latency, and
routing decisions. That data exists on OpenRouter's servers for every Pi
session the factory runs. Today the two data sets are parallel and
uncorrelated: the factory cannot tell OpenRouter which project or session a
request belongs to, and you cannot navigate from a local usage record
to the corresponding server-side view.

Three needs follow:

1. **Session-level grouping in the provider's UI.** OpenRouter's
   `logs?tab=sessions` view groups requests by a caller-supplied `session_id`.
   Pi sessions through the factory currently appear as isolated, ungrouped
   requests. You debugging a run must correlate by timestamp and model,
   not by a shared identifier.

2. **Project-level cost attribution.** The factory's local records carry
   `project_id` and `project_name` in every record, but OpenRouter has no
   concept of "project." Requests from all factory projects on the same
   OpenRouter account appear in one undifferentiated stream. There is no way to
   answer "how much did project X spend last month?" from OpenRouter's data
   without manual correlation.

3. **Budget enforcement at the provider.** The token-usage-tracking proposal
   explicitly deferred budget enforcement. OpenRouter offers per-key credit
   limits with automatic reset — a budget enforcement layer at zero
   implementation cost, if the factory provisions one key per project.

Dollar-cost math (provider-reported spend × model × rate table) was also
deferred in the token-usage-tracking proposal. OpenRouter's per-key usage
counters and analytics API provide exactly that layer, but only if requests are
attributed to a key the factory controls.

## Core Principles

- **No network calls on the runtime path.** Session injection is a local
  request-body mutation in a Pi extension. Key injection is an environment
  variable read from a local file. Neither makes a network call or adds a
  failure mode to agent dispatch.

- **No network calls in `init-factory`.** Key provisioning is a separate
  curation tool, invoked on demand, following the precedent of
  `openrouter-discover`. `init-factory` installs the session extension via
  symlink — the same mechanism it uses for every other Pi extension.

- **Verify before building.** Two assumptions underpin the design: that Pi's
  `before_provider_request` hook allows body mutation that reaches OpenRouter,
  and that Pi's authentication resolution order permits environment-variable
  key override. Both must be confirmed by executable experiment before
  implementation begins.

- **Complementary, not competing, data.** The local JSONL system and
  OpenRouter's server-side accounting answer different questions. They are
  scoped, not reconciled. Local records are authoritative for cross-CLI
  comparable token counts; OpenRouter is authoritative for actual dollar cost,
  provider routing, and cache behaviour. Neither replaces the other.

## Design

### Phase 0 — Verification

Two manual experiments, producing findings (not code):

**V-1: `before_provider_request` round-trip.** Write a minimal Pi extension
that injects a known `session_id` value into `event.body` in the
`before_provider_request` handler. Make one OpenRouter request. Query
`GET /api/v1/generation?id=<gen_id>` and confirm the `session_id` field on the
generation record matches the injected value. This confirms the full path:
Pi extension → request body mutation → OpenRouter storage → generation
metadata → logs/sessions view.

**V-2: Pi authentication resolution order.** Determine whether
`OPENROUTER_API_KEY` set in the process environment takes precedence over a key
configured in `~/.pi/agent/auth.json` (or vice versa). Spawn `pi` with both
configured (different keys) and check which key OpenRouter sees. This decides
whether environment-variable override is a viable key-injection mechanism for
subagent spawns via `run-agent.ts` and `dispatch-wave.ts`.

Both are single-session, single-request experiments. They produce documented
findings, filed under `docs/findings/`.

### Phase 1 — Session Injection

A factory-owned Pi extension that injects `session_id` into every
OpenRouter-routed request, using the factory's session identity with project
context.

**Extension:** `factory/config/extensions/openrouter-session.ts`. Hooks two
Pi events:

- `session_start`: captures the factory session ID via `activeSessionId()`
  from the shared `pi-usage.ts` helpers, and reads `config/project.json` for
  the project slug and ID prefix.
- `before_provider_request`: guards on `openrouter` in the model string,
  then sets `event.body.session_id` to a composite value.

**Composite session_id format:**
`{project_slug}:{project_id_prefix}:{factory_session_id}`

Example: `my-service:550e8400:pi-a1b2c3d4-5678-...`

The composite format serves three purposes: project attribution in the
sessions view without requiring per-project API keys, textual filterability
in the OpenRouter UI, and direct correlation with the `session_id` field in
local `.agent-factory/usage/*.jsonl` records (the third segment).

For subagent spawns (`run-agent.ts`, `dispatch-wave.ts`): the factory already
sets `PI_AGENT_FACTORY_SESSION_ID` in the child environment. The extension
picks that up via the existing `activeSessionId()` resolver. The child's
`session_id` carries the child session's factory ID with the same project
prefix, preserving the tree structure in the sessions view.

**Installation:** `init-factory` symlinks the extension into
`.pi/extensions/`, exactly as it does for `capture-usage.ts`,
`block-dangerous-git.ts`, `run-agent.ts`, and `dispatch-wave.ts`.
`remove-factory` removes the symlink. No new mechanism.

**What this buys immediately:** Every Pi session in the factory appears in
`openrouter.ai/logs?tab=sessions`, grouped by conversation, labelled with the
project name and factory session ID. You clicks through to see every
model call in a run — costs, tokens, latency, provider, cache hits — without
leaving the OpenRouter UI. No API key management, no analytics queries, no
beta APIs.

### Phase 2 — Per-Project API Key Provisioning

A separate curation tool, `factory/scripts/openrouter-provision`, following
the same pattern as `openrouter-discover`: you aid, off the runtime
path, stdlib-only, optional. Requires `OPENROUTER_MANAGEMENT_KEY` in the
environment.

**Commands:**

| Command           | What it does                                                                                                                                                                                             |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--action create` | Provisions a key via `POST /api/v1/keys`, stores the hash in `config/project.json`, stores the key value in `.agent-factory/credentials/openrouter-key` (0600). Refuses if a key is already provisioned. |
| `--action check`  | Verifies the stored hash exists and is enabled server-side. Exit 0 if ok, exit 1 if missing/disabled. A drift gate, like `openrouter-discover --check`.                                                  |
| `--action rotate` | Creates a new key, updates the stored credential, disables (not deletes) the old key. The old key remains for audit trail; it stops accepting requests but its usage history is preserved.               |
| `--action revoke` | Disables the key server-side and removes the local credential. Leaves the hash in `project.json` marked `"openrouter_key_status": "revoked"` for audit reference.                                        |

**Key naming convention:** `agent-factory:{project_name} ({project_id[:8]})`

**Storage layout:**

- `config/project.json` gains `openrouter_key_hash` (the 64-char hex hash
  returned by OpenRouter). Non-secret. Gitignored (as `config/project.json`
  already is).
- `.agent-factory/credentials/openrouter-key` stores the key value (`sk-or-v1-...`).
  Mode 0600. Gitignored. Not readable by agents — only by spawn-time
  infrastructure in `run-agent.ts` / `dispatch-wave.ts`.

**Key injection for subagents:** Conditional on V-2 confirming environment
variable precedence. The shared helper in `pi-usage.ts` reads the credential
file; `run-agent.ts` and `dispatch-wave.ts` set `OPENROUTER_API_KEY` in the
child's environment. Root human sessions remain you's
responsibility — `openrouter-provision --action create` emits a reminder:
"To use this project's OpenRouter key in interactive sessions, run:
`export OPENROUTER_API_KEY=$(cat .agent-factory/credentials/openrouter-key)`"

If V-2 shows Pi resolves `auth.json` over the environment variable, the
injection mechanism must be revised — likely writing a project-scoped
`auth.json` or using a Pi CLI flag if one exists. That design decision is
deferred to the V-2 finding.

**Management key scope:** `OPENROUTER_MANAGEMENT_KEY` can create, delete,
and modify all keys on the account. It is a high-privilege credential. The
proposal confines it to you-invoked provisioning tool; it never
appears on the runtime path, in `init-factory`, or in any agent-accessible
location.

**Budget enforcement:** Each provisioned key can carry a credit `limit` with
`limit_reset` (daily/weekly/monthly). The `--action create` command accepts
optional `--limit` and `--limit-reset` flags. OpenRouter enforces the budget
server-side by rejecting requests when the limit is reached. This is the
budget enforcement layer the token-usage-tracking proposal deferred, provided
at zero implementation cost by the provider.

**Analytics integration:** With one key per project, the OpenRouter analytics
API's `api_key_id` dimension directly maps to project identity. Spend per
project is a single query filtered by `api_key_id`.

### Phase 3 — Usage Query Tool (Deferred)

`factory/scripts/openrouter-usage` — a query tool against OpenRouter's
analytics API, filtered by the project's key hash. Deferred until:

1. The analytics API exits beta (OpenRouter labels it `beta.Analytics`;
   behavioural details "can drift"), or
2. Sufficient operational experience with Phase 1 and Phase 2 establishes
   which queries actually matter.

In the interim, the OpenRouter dashboard UI over the sessions view (Phase 1)
and the per-key usage counters visible via `GET /api/v1/keys/{hash}`
(Phase 2) cover the immediate need. The dashboard is OpenRouter's product;
the factory should not replicate it prematurely.

When built, the tool's authority partition is:

| Concern                                 | Authoritative source                         | Rationale                                     |
| --------------------------------------- | -------------------------------------------- | --------------------------------------------- |
| Cross-CLI comparable token counts       | Local JSONL, `cl100k_base`                   | One fixed tokenizer, offline, deterministic   |
| Actual dollar cost                      | OpenRouter (key usage counters or analytics) | OpenRouter knows the rate table               |
| Session structure and agent correlation | Local JSONL                                  | Factory session IDs, agent names, phase, loop |
| Per-request latency, routing, cache     | OpenRouter (generation metadata)             | Provider-side measurement                     |

## Scope

**In the first release (Phases 0–2):**

- V-1 and V-2 verification experiments and their documented findings.
- `factory/config/extensions/openrouter-session.ts`: the `before_provider_request`
  session injection extension.
- `init-factory` and `remove-factory` updated to install/remove the extension
  symlink into `.pi/extensions/`.
- `factory/scripts/openrouter-provision`: the per-project key lifecycle tool
  (create, check, rotate, revoke).
- `config/project.json` schema extended with `openrouter_key_hash` and
  `openrouter_key_status`.
- `.agent-factory/credentials/` directory and `openrouter-key` file, created
  by the provisioning tool, secured by `init-factory`'s existing
  `_private_directory` / `_private_file` infrastructure.
- Key injection in `run-agent.ts` and `dispatch-wave.ts` child environments,
  conditional on V-2.
- Tests: round-trip session-id injection (synthetic Pi extension test),
  provisioning tool CLI modes (against a fixture or mock), key-injection
  env-var propagation in subagent spawns.

**Explicitly deferred (do NOT plan stories for these):**

- `openrouter-usage` analytics query tool (Phase 3). Depends on analytics API
  stability.
- Dollar-cost math or rate-table integration. OpenRouter owns the rate table;
  the factory does not replicate it.
- Workspace-level OpenRouter integration. Workspaces are an organizational
  boundary, not a project boundary; overkill for per-project tracking.
- OpenRouter classifier integration. Custom taxonomies for tagging generations
  require workspace-level classifier setup and add latency to every request.
- Session injection for non-Pi CLIs. Claude Code, Copilot CLI, and Codex do
  not route through OpenRouter. If they later do, the session extension
  pattern applies but the hook mechanism differs.
- Automatic key injection for root human Pi sessions. Enforcement for
  interactive sessions requires process discipline (shell profile, `.envrc`),
  not factory infrastructure. The provisioning tool emits a reminder.
- OpenRouter Broadcast / observability platform integration. The `session_id`
  and `trace` fields in request bodies are forwarded to configured broadcast
  destinations. This is a valuable capability but orthogonal to this proposal.

## Design Details

### Naming and format of the composite session_id

The composite format is: `{slug}:{id_prefix}:{factory_session_id}`.

- `slug`: the `project_name` from `config/project.json`, lowercased,
  non-alphanumeric characters replaced with hyphens, capped at 40 characters.
- `id_prefix`: the first 8 characters of the `project_id` UUID.
- `factory_session_id`: the value from `activeSessionId()`, unchanged.

The cap at 40 + 1 + 8 + 1 + factory-session-id keeps the total well within
OpenRouter's 256-character `session_id` limit. A Pi session ID
(`pi-<uuid4>`) is 39 characters; the composite is under 90.

If `config/project.json` is absent or unreadable, the extension degrades to
injecting only the factory session ID, without project context. Session
injection never fails a request.

### Interaction with `pi-openrouter-session` (community extension)

The community extension `pi-openrouter-session` (npm package) hooks the same
`before_provider_request` event. If you installs both, the last
writer wins — Pi's `before_provider_request` handlers run in extension load
order. The factory extension should document this incompatibility. The two
extensions are not composable because they both set `event.body.session_id`.

### Interaction with token-usage-tracking

This proposal extends, not replaces, the implemented token-usage-tracking
system. Local JSONL records continue unchanged. The `session_id` in the
composite OpenRouter value's third segment is the same value as the
`session_id` field in the local record. Correlation is by shared identifier,
not by reconciling token counts (which will never match, because `cl100k_base`
and the model's native tokenizer produce different counts for the same text).

### Interaction with `openrouter-discover`

`openrouter-discover` curates `model.conf` tier rows from the OpenRouter
catalog. It reads model metadata; it does not read or write usage data.
`openrouter-provision` manages API keys. The two tools share the pattern
(curation tool, off the runtime path, stdlib-only, optional
`OPENROUTER_API_KEY` / `OPENROUTER_MANAGEMENT_KEY`) but have disjoint
responsibilities.

### Failure behaviour of the session extension

The extension is best-effort. If `config/project.json` is unreadable, the
extension injects the bare factory session ID. If `activeSessionId()` returns
no value, the extension does nothing. If body mutation silently fails (e.g.,
event object is frozen), the request proceeds without `session_id`. No
failure in the extension may fail, block, or slow the measured run — the same
principle as `usage-capture`.

### Credential lifecycle

| Event                                  | Effect on local credential                                               | Effect on OpenRouter                            |
| -------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------- |
| `openrouter-provision --action create` | File created, 0600                                                       | Key created, active                             |
| `openrouter-provision --action rotate` | File updated with new key                                                | Old key disabled, new key active                |
| `openrouter-provision --action revoke` | File removed                                                             | Key disabled                                    |
| `remove-factory`                       | `.agent-factory/credentials/` removed with the rest of `.agent-factory/` | No effect — orphaned key remains on the account |

The `remove-factory` orphan is a known limitation. `remove-factory` is a
local operation; it does not make network calls. You who removes the
factory and wants to clean up the OpenRouter key must run
`openrouter-provision --action revoke` before `remove-factory`, or delete the
key manually in the OpenRouter dashboard. The provisioning tool's `--action check` drift gate surfaces orphaned keys when run against a re-initialized
project that finds a hash but no server-side key.

### Security of `.agent-factory/credentials/`

The directory inherits `init-factory`'s existing `_private_directory` (0700)
and `_private_file` (0600) infrastructure. The credential file is:

- Gitignored (covered by the existing `.agent-factory/` gitignore entry).
- Owner-only readable (0600, repaired by `_repair_private_tree`).
- Not symlink-followed (created with `O_NOFOLLOW` semantics).
- Not readable by agents — agents interact with the factory through skills,
  tools, and the orchestrator, none of which expose the credentials directory.

The management key (`OPENROUTER_MANAGEMENT_KEY`) is never stored on disk by
the factory. It exists only in you's environment for the duration of
a provisioning command.

## Open Questions

- **Does V-2 confirm environment-variable precedence for Pi's OpenRouter
  authentication?** If not, the key-injection mechanism for subagent spawns
  must be redesigned. Possible alternatives: project-local `auth.json`,
  Pi CLI flag, or Pi configuration file override. This question blocks
  Phase 2 key injection but not Phase 1 session injection.

- **Should the provisioning tool set a default credit limit?** A key with no
  limit is unbounded. The tool could require `--limit` on create, or default
  to a conservative value with `--no-limit` as the explicit opt-out. This is
  a policy decision, not a technical one.

- **Is `before_provider_request` body mutation a stable Pi extension API
  contract?** The community extension `pi-openrouter-session` relies on it
  and has been published since May 2026. V-1 confirms it works today. But
  Pi's extension API has no stability guarantee. If the hook semantics
  change, the factory extension breaks. Mitigation: the extension is a
  single file, isolated, best-effort — a breakage degrades to no session
  attribution, not to failed requests.

## Completion Criteria

- V-1 finding documents the `before_provider_request` → OpenRouter
  `session_id` round-trip with a reproducible procedure and result.
- V-2 finding documents Pi's authentication resolution order for OpenRouter
  with a reproducible procedure and result.
- `factory/config/extensions/openrouter-session.ts` injects a composite
  `session_id` into every OpenRouter-routed request, with project context
  from `config/project.json` and session identity from `activeSessionId()`.
- `init-factory` installs the session extension symlink into
  `.pi/extensions/`; `remove-factory` removes it. Both are idempotent. No
  network call is added to either.
- `factory/scripts/openrouter-provision` implements create, check, rotate,
  and revoke. Each mode is tested against a fixture or mock (no live
  OpenRouter calls in automated tests).
- `config/project.json` accepts `openrouter_key_hash` and
  `openrouter_key_status` without breaking existing consumers
  (`init-factory`, `remove-factory`, `usage-capture`).
- Subagent spawns via `run-agent.ts` and `dispatch-wave.ts` inject the
  project's OpenRouter key into the child environment when the credential
  file exists (conditional on V-2).
- No failure in the session extension or key injection fails, blocks, or
  slows any agent run. Best-effort principle holds.

## Guiding Rule

The factory already knows what it spent; this feature lets the provider
confirm it.
