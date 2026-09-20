---
scope: global
---

# Entity Model — Factory Flow Control

The entities `factory/scripts/transition-lint`, `factory/scripts/phase`, `factory/scripts/trigger`, and `factory/scripts/index-lint` read, write, or generate, and how they relate. Applying **SOLID** (Single Responsibility): each entity owns one concern of the run's state — the marker owns *where a run is*, the FSM definition owns *what the run's phases are*, the catalog owns *what agents/skills/playbooks/rulebooks exist*.

```mermaid
erDiagram
    FSM_DEFINITION ||--o{ STATE_DEFINITION : declares
    FSM_DEFINITION ||--o{ HALT_CONDITION : declares
    FSM_DEFINITION ||--o{ GATE_CONDITION : "gate_conditions library"
    STATE_DEFINITION ||--o{ GATE_CONDITION : "entry_conditions reference"
    HALT_CONDITION }o--|| STATE_DEFINITION : caps
    PLAYBOOK_STATE_MARKER }o--|| FSM_DEFINITION : "instance of (by playbook name)"
    PLAYBOOK_STATE_MARKER }o--|| STATE_DEFINITION : "currently at (by state name)"
    GATE_CONDITION ||--o{ FINDING : "no_open_findings counts"
    CATALOG ||--o{ AGENT_ENTRY : lists
    CATALOG ||--o{ SKILL_ENTRY : lists
    CATALOG ||--o{ PLAYBOOK_ENTRY : lists
    CATALOG ||--o{ RULEBOOK_ENTRY : lists
    PLAYBOOK_ENTRY ||--o| FSM_DEFINITION : "fsm field points at"
    PLAYBOOK_ENTRY ||--o{ AGENT_ENTRY : "agents sequence"
    AGENT_ENTRY ||--o| MODEL_MATRIX_ENTRY : "tier resolves via"
    HANDOFF ||--o{ ARTIFACT_REFERENCE : names
    HANDOFF ||--|| REPOSITORY_STATE : records
    HANDOFF_SEMANTIC_REVIEW }o--|| HANDOFF : evaluates
    CHILD_RESULT_ENVELOPE ||--o{ ARTIFACT_REFERENCE : points_to
    SESSION_USAGE_SIGNAL }o--|| REPOSITORY_STATE : qualifies_session

    FSM_DEFINITION {
        string playbook
        string version
        string type "workflow-state-machine"
    }
    STATE_DEFINITION {
        string name
        string description
        string agent "nullable — null for a human-approval state"
        string session "stateful or stateless, nullable"
        list   outputs "glob patterns"
        list   entry_conditions "gate_conditions names"
        bool   final "nullable, true on the terminal state"
    }
    GATE_CONDITION {
        string name
        string type "file_exists | files_exist | no_open_findings | script_exit_zero"
        string path "nullable — file_exists"
        list   paths "nullable — files_exist"
        string pattern "nullable — no_open_findings, single glob"
        list   patterns "nullable — no_open_findings, multiple globs"
        string script "nullable — script_exit_zero, stubbed to pass"
    }
    HALT_CONDITION {
        string type "max_iterations | script_failure | circular_dependency"
        string state "nullable — the state max_iterations names"
        string event "nullable"
        int    limit "nullable — max_iterations only"
        string message "nullable — human escalation text"
    }
    PLAYBOOK_STATE_MARKER {
        string playbook
        string state
        string gate "nullable"
        string result "pass, nullable"
        int    open_findings
        string next "nullable — next state name"
        int    iteration
        string recorded_by "human or an agent/CLI identifier"
        string recorded_at "UTC timestamp, ISO 8601, script clock only"
    }
    FINDING {
        string id "TAG-NNNN"
        string status "open | resolved, frontmatter field"
    }
    CATALOG {
        string generated_by "index-lint"
    }
    AGENT_ENTRY {
        string name
        string title
        string tier "nullable — economy | standard | strong"
        string description
        string path
        int    tokens "tiktoken cl100k_base body count"
        int    total_tokens "body + skills + rulebooks"
        object inputs "required and context subkeys"
        object outputs "minimum_changed and declarations"
    }
    SKILL_ENTRY {
        string name
        string category "nullable"
        string description
        string path
        int    tokens "tiktoken cl100k_base body count"
    }
    PLAYBOOK_ENTRY {
        string name
        string title
        string category "nullable"
        string description
        string path
        string fsm "nullable — path to the .fsm.yml"
        int    tokens "tiktoken cl100k_base body count"
        int    total_tokens "nullable — body + unique agent totals"
    }
    RULEBOOK_ENTRY {
        string name
        string category "nullable — e.g. conventions"
        string path
        int    tokens "tiktoken cl100k_base body count"
    }
    MODEL_MATRIX_ENTRY {
        string cli "copilot | codex | pi (model.conf row keys. Claude Code resolves its model outside model.conf)"
        string tier "economy | standard | strong"
        string model_id
    }
    HANDOFF {
        string outgoing_phase
        string incoming_phase
        string summary "dense, no information loss"
        string next_action
    }
    HANDOFF_SEMANTIC_REVIEW {
        string reviewer
        string disposition "pass or reject"
        list omissions_or_distortions
    }
    ARTIFACT_REFERENCE {
        string path "canonical tracked path"
        string purpose
    }
    REPOSITORY_STATE {
        string head_sha "exact 40-character SHA"
        string branch
        string upstream
        string gate_result
        string verification_evidence
    }
    CHILD_RESULT_ENVELOPE {
        string disposition
        map finding_counts "by severity"
        string next_action "one to three sentences"
    }
    SESSION_USAGE_SIGNAL {
        string cli
        string provider
        string capability "full-cache | input-only | unavailable"
        int cache_miss_turns "nullable when unavailable"
        int cache_miss_input_tokens "nullable when unavailable"
        float late_early_input_ratio "nullable when unavailable"
    }
    SCOPE_MAP_ROW {
        string rule "behavioral claim — one sentence"
        string status "implemented | specified | deferred"
        string confidence "nullable — verified | flagged | high | medium-high | medium | medium-low | low | lowest | claimed"
        string sources "spec or evidence origin — UC file, .feature file, test file, doc"
        string feature_link "nullable — path to implementing code#59; anchors conceptual rule to codebase"
    }
    ANCHOR_FILE_SET {
        string architecture_dsl "docs/arc42/architecture.dsl"
        string scope_map "docs/spec/scope-map.md"
        string context "docs/CONTEXT.md"
    }
```

## Notes

- **FSM_DEFINITION** is one `factory/playbooks/<name>.fsm.yml` file. Only `greenfield-development` has one today — see [PRD § NG4](../prd.md#non-goals). `phase advance`, `phase retry`, and `transition-lint` each parse it independently with the same minimal, indentation-based subset parser (block mappings, block sequences including sequences of multi-key mappings, inline comments, scalars) — not a general YAML library, matching this repo's zero-dependency convention.
- **STATE_DEFINITION.outputs** is a list of glob patterns (`*` within a segment, `**` across segments, `?` one non-separator character) that `transition-lint` matches staged file paths against, and `run-step` matches on-disk files against, to decide state ownership.
- **GATE_CONDITION.type = script_exit_zero** is stubbed to always pass in the current implementation — a named, deferred gap. See [T-03](../todos.md#t-03-script_exit_zero-condition-type-is-stubbed--partially-resolved).
- **HALT_CONDITION** of type `max_iterations` is the only type `phase retry` currently enforces; `script_failure` and `circular_dependency` are declared in `greenfield-development.fsm.yml` but have no enforcing script yet — see [T-04](../todos.md#t-04-halt_conditions-types-other-than-max_iterations-are-unenforced).
- **PLAYBOOK_STATE_MARKER** is the single source of truth for "where is this run" — one flat file at `.current-work/playbook-state.yml`, git-ignored. Full field-level rules in [validation-rules.md](validation-rules.md).
- **FINDING.status** is read from the finding file's YAML frontmatter (a `---`-delimited block whose first line is exactly `---`); `no_open_findings` conditions count files matching a glob whose `status` is exactly `open`. Filing conventions: [finding-format.md § When to file](../../../factory/rulebooks/conventions/finding-format.md#when-to-file).
- **CATALOG** is `factory/INDEX.yaml` — one file holding four entry types (agents, skills, playbooks, rulebooks). It is generated wholesale on every `index-lint` run; there is no per-entry incremental update. Every entry carries a `tokens` field; agents and playbooks also carry `total_tokens`.
- **AGENT_ENTRY.tier** and **MODEL_MATRIX_ENTRY.tier** share the same three-value vocabulary (`economy | standard | strong`); `trigger` resolves an agent's dispatch model by looking up `<cli>.<tier>` in `config/model.conf`.
- **HANDOFF** is the restart contract between two phases. It owns phase continuity; **REPOSITORY_STATE** owns the exact revision and validation evidence, and **ARTIFACT_REFERENCE** names durable information instead of embedding it in a transcript. **HANDOFF_SEMANTIC_REVIEW** records the separate human/agent judgment that the mechanically valid handoff omitted or distorted no material fact.
- **DISPATCH_LEDGER** is the script-owned dispatch record at `.current-work/<feature-branch>/dispatch-ledger.yaml`; each story entry tracks lifecycle fields including `tier`, `attempts`, and the pre-spawn `prepared` state, and each `WaveCloseout` entry records a wave summary (`number`, `completed`, `blocked`, `failed`, `next_ready`, `branch_head`).
- **CHILD_RESULT_ENVELOPE** is deliberately smaller than the tracked result it references. **SESSION_USAGE_SIGNAL** is retrospective evidence qualified by CLI/provider, never live workflow state.
- **SCOPE_MAP_ROW** is one row in `docs/spec/scope-map.md`. The table always has five columns: Rule, Status, Confidence, Sources, Feature Link. `confidence` is populated by the `reverse-map` skill during brownfield onboarding; rows created by `derive-feature` or `scope-map-migration` leave it empty. `sources` names the spec or evidence origin (UC file, .feature file, test file). `feature_link` anchors the conceptual rule to the implementing code — the bridge between the specification plane and the codebase. It is empty when the rule is `specified` (not yet implemented) or when the implementing code has not been identified; the `reconciliation-agent` fills it after implementation. The confidence hierarchy follows a forensic evidence model: passing tests are `verified`, code entry points are `high`, external docs are progressively lower. See [newcomer-onboarding.feature](../newcomer-onboarding.feature).
- **ANCHOR_FILE_SET** is the minimum prerequisite for `feature-addition` after brownfield-lite onboarding. The three files are checked by file existence, not by a gate marker. Their presence signals readiness for feature work; their absence suggests running `brownfield-onboarding` first.

## Test-Design Entities

The test-design skill introduces entities that bridge the specification plane (`.feature` contracts, scope map) to the planning plane (`backlog/epics.md`, story files). These entities are document structures within `backlog/epics.md` and `backlog/ST-NNNN.md`, not database records.

```mermaid
erDiagram
    EPIC_BUILDING_BLOCK ||--o{ TEST_DESIGN_SECTION : "gains (when test-design runs)"
    EPIC_BUILDING_BLOCK ||--o{ PRIOR_TESTS_SECTION : "gains (for non-owning stories)"
    TEST_DESIGN_SECTION ||--|| RISK_CLASS : "classified by"
    TEST_DESIGN_SECTION ||--o{ FAILURE_SCENARIO : "contains"
    TEST_DESIGN_SECTION ||--o{ WAIVER : "may contain"
    PRIOR_TESTS_SECTION ||--o{ TEST_REFERENCE : "lists"
    RISK_CLASS_CONFIG }o--|| RISK_CLASS : "overrides defaults for"
    GATE_CONFIG ||--o{ GATE_ENTRY : "contains"
    SCOPE_MAP_ROW }o--|| TEST_DESIGN_SECTION : "traced from (via trace ID)"

    RISK_CLASS {
        string name "critical | standard | structural | custom"
        string format "forbidden | scenario | linter"
        string budget "unbounded | equivalence"
        list requires "optional — named invariants"
    }
    RISK_CLASS_CONFIG {
        string source "testing.yaml risk_classes section"
        string precedence "testing.yaml > strategy doc > Factory convention"
    }
    TEST_DESIGN_SECTION {
        string contract_id "trace ID e.g. DOM-01"
        string risk_class "critical | standard | structural"
        string layer "contract_test | integration_test | etc."
        list failure_scenarios "Given/When/Then[/Forbidden] blocks"
    }
    PRIOR_TESTS_SECTION {
        string contract_id "trace ID"
        list test_references "module::function pairs from owning story"
    }
    FAILURE_SCENARIO {
        string given "precondition"
        string when "action"
        string then "expected outcome"
        string forbidden "nullable — specific failure mode (critical only)"
    }
    WAIVER {
        string contract_id "trace ID"
        string owner_path "tests/test_module.py::test_function"
        string format "blockquote line in Test Design section"
    }
    TEST_REFERENCE {
        string module "test file path"
        string function "specific test function name"
    }
    GATE_CONFIG {
        string source "docs/testing.yaml gates section"
    }
    GATE_ENTRY {
        string name "crap_score | mutation_testing | test_design_verify"
        bool enabled "true | false"
        float threshold "nullable — gate-specific"
    }
```

### Notes

- **RISK_CLASS** has three Factory convention defaults (`critical`, `standard`, `structural`). Projects may add custom classes in `docs/testing.yaml`'s `risk_classes:` section. Precedence: `testing.yaml` inline > project-linked strategy document > Factory convention defaults.
- **TEST_DESIGN_SECTION** is a markdown section (`#### Test Design`) within a story's building-block entry in `backlog/epics.md`. It is carried verbatim into the corresponding `backlog/ST-NNNN.md` by `create-backlog-stories`.
- **PRIOR_TESTS_SECTION** is a markdown section (`#### Prior Tests`) for non-owning stories. The developer-agent runs these tests first and must keep them green.
- **WAIVER** is a blockquote line within the `#### Test Design` section: `> Waiver: DOM-01 — owned by tests/test_domain.py::test_entity_uniqueness`. The `test-design-verify` gate parses these and validates the named test module exists.
- **GATE_CONFIG** is a new section in `docs/testing.yaml` that centralizes gate configuration. It does not define gate execution ordering — [ADR-0012](../../adr/0012-dispatcher-owned-semantic-gate-loop.md) owns the dispatcher's gate sequence.
- **GATE_ENTRY** configures an individual gate. `test_design_verify` is implicitly enabled when test-design output exists in the story and skipped otherwise.

## Agent Context Entities

The concern registry is the factory-facing routing interface to project knowledge. Machine-consumed test configuration remains a separate artifact.

```mermaid
erDiagram
    CONCERN_REGISTRY ||--o{ CONCERN_ENTRY : contains
    CONCERN_ENTRY ||--|{ ROUTED_PATH : routes
    STORY }o--o{ CONCERN_ENTRY : references
    CTX_FINDING }o--|| CONCERN_REGISTRY : validates
    TESTING_YAML }o--|| TEST_SUITE : configures

    CONCERN_REGISTRY {
        string path "docs/agent-context.md"
        string format "CLI-agnostic markdown"
    }
    CONCERN_ENTRY {
        string category "cross-cutting | technical | domain"
        string name "controlled vocabulary"
        string description
    }
    ROUTED_PATH {
        string kind "Read | Boundary"
        string path "repository-relative file or glob"
    }
    STORY {
        string path "backlog/ST-NNNN.md"
        list domain_concerns
        list technical_concerns
    }
    TESTING_YAML {
        string path "docs/testing.yaml"
        string role "machine-consumed test configuration"
        string writer "detect-test-regime (sole owner)"
    }
    TEST_SUITE {
        string name
        string command
    }
    CTX_FINDING {
        string code "CTX-SECTIONS | CTX-PATHS | CTX-REFS | CTX-LEGACY"
        string severity "error"
        string message "human-readable finding text"
    }
```

### Notes

- **CONCERN_REGISTRY** has exactly three category headings: Always (cross-cutting), Technical concerns, and Domain concerns.
- **CONCERN_ENTRY** has a description and at least one `Read:` path. `Boundary:` paths are optional. Cross-cutting entries always apply; story frontmatter selects technical and domain entries.
- **STORY.concerns** is advisory and uses only confirmed registry headings. A missing vocabulary entry is proposed and confirmed before use.
- **TESTING_YAML** is not routing content. Factory consumers resolve only `docs/testing.yaml`; there is no legacy-path fallback.
- **CTX_FINDING** is produced by `concern-lint`. Legacy YAML context or `docs/charter/` beside the registry is an error.

## Referenced from

- [actor-goal-list.md](../../~archive/spec/actor-goal-list.md)
- [UC-01](../../~archive/spec/use_cases/UC-01-advance-a-playbook-phase.md)
- [test-design.feature](../test-design.feature)
- [agent-context.feature](../agent-context.feature)

## Local Usage Analysis Entities

The [local usage feature](../local-usage-processing-and-analysis.feature) retains JSONL as evidence and creates query-scoped analytical entities only.

```mermaid
erDiagram
    USAGE_RECORD_CONTRACT ||--o{ USAGE_RECORD : validates
    INPUT_SET ||--o{ USAGE_RECORD : selects
    INPUT_SET ||--o{ PREFLIGHT_FAILURE : detects
    USAGE_RECORD ||--|| RAW_USAGE_SNAPSHOT : types
    RAW_USAGE_SNAPSHOT }o--|| LOGICAL_RUN : identifies
    LOGICAL_RUN ||--|| LATEST_RUN_SNAPSHOT : reduces_to
    LATEST_RUN_SNAPSHOT }o--|| CANONICAL_SESSION_USAGE : conserves_into
    CANONICAL_SESSION_USAGE ||--o{ DIMENSIONAL_USAGE : aggregates
    CANONICAL_SESSION_USAGE ||--o{ CACHE_EFFICIENCY_SIGNAL : qualifies
    INPUT_SET ||--|| CAPTURE_HEALTH : summarizes
    PUBLISHED_VIEW ||--o{ QUERY_RESULT : produces
    QUERY_RESULT ||--o| PARQUET_EXPORT : exports
    INSTALLED_COMPONENT ||--|| INSTALLED_CONTRACT_COPY : contains
    USAGE_RECORD_CONTRACT ||--|| INSTALLED_CONTRACT_COPY : projects

    USAGE_RECORD_CONTRACT {
        string owner
        string current_version
        string compatibility_policy
        string accepted_consumer_range
        string schema_dialect
    }
    INPUT_SET {
        list sorted_top_level_paths
        string input_set_digest
        string usage_directory
        datetime snapshotted_at
    }
    USAGE_RECORD {
        string source_file
        integer source_line
        string cli
        string session_id
        string run_id
        string parent_run_id
        integer capture_sequence
        integer normalized_input
        integer normalized_output
        integer normalized_total
    }
    PREFLIGHT_FAILURE {
        string source_file
        integer source_line
        string field
        string failure_code
    }
    RAW_USAGE_SNAPSHOT {
        string evidence_identity
        string typed_schema
    }
    LOGICAL_RUN {
        string logical_run_key
        string session_id
        string parent_run_id
    }
    LATEST_RUN_SNAPSHOT {
        string logical_run_key
        integer capture_sequence
        string normalized_source_path
        integer source_line
    }
    CANONICAL_SESSION_USAGE {
        string session_id
        string accounting_rule
        integer normalized_total
    }
    DIMENSIONAL_USAGE {
        string time_granularity
        string dimensions
        datetime period_start
        integer additive_total
    }
    CACHE_EFFICIENCY_SIGNAL {
        string provider
        string availability_state
        integer cached_tokens
    }
    CAPTURE_HEALTH {
        integer valid_count
        integer failure_count
        string failure_code
        string source_file
    }
    PUBLISHED_VIEW {
        string name
        string schema
        string query_model_version
    }
    QUERY_RESULT {
        string format
        string schema
        string logical_rows
    }
    PARQUET_EXPORT {
        string destination
        string query_model_version
        string input_set_digest
        string replacement_state
    }
    INSTALLED_COMPONENT {
        string name
        string source_commit
        string version
        datetime installed_at
    }
    INSTALLED_CONTRACT_COPY {
        string version
        string accepted_range
    }
```

### Entity invariants

- `INPUT_SET` is immutable for one query and contains only sorted, top-level `*.jsonl` paths from the selected usage directory.
- Evidence identity is `(normalized_source_path, source_line)`. The path is relative to the selected usage directory, uses `/` separators, has `.` removed, rejects `..`, absolute paths, invalid UTF-8, and Unicode-normalizes each segment to NFC. Line numbers are one-based positive integers.
- The closed registry keys are exactly `claude-code`, `pi`, `codex`, and `copilot`. Every CLI uses logical-run key `(cli, session_id, run_id)`. For Claude Code and Pi this distinguishes additive child or descendant runs; for Codex and GitHub Copilot CLI it distinguishes inclusive roots from attribution-only descendants. `parent_run_id` establishes ancestry but is not part of identity. Source path, source line, capture sequence, and record content never enter the logical-run key.
- Before `LATEST_RUN_SNAPSHOT` selection, all otherwise valid evidence snapshots for one logical-run key must have exactly one distinct `parent_run_id`, with null treated as a value. Disagreement classifies every snapshot for that key as a `PREFLIGHT_FAILURE` with `USAGE_ANCESTRY_PARENT_CONFLICT`; no evidence snapshot establishes or overrides the logical run's parent.
- Each `(cli, session_id)` partition contains exactly one root with null `parent_run_id`. Every non-root parent resolves to a distinct logical run in the same partition. The parent graph is acyclic, every run is reachable from the root, direct children name the root's `run_id`, and descendants are its transitive closure.
- Missing parents, cross-CLI or cross-session parents, self-links, cycles, and root counts other than one create `PREFLIGHT_FAILURE` rows with the stable `USAGE_ANCESTRY_*` codes and prevent canonical accounting.
- Every selected line produces exactly one `USAGE_RECORD` or `PREFLIGHT_FAILURE` in query scope.
- `normalized_total` equals `normalized_input + normalized_output`; token counters are non-negative.
- `LATEST_RUN_SNAPSHOT` selects the greatest tuple `(capture_sequence, normalized_source_path, source_line)`: capture sequence numerically ascending, normalized path by unsigned UTF-8 byte lexicographic order, and line number numerically ascending. Selection takes the maximum tuple; this makes the later line win within one file and removes source identity after one snapshot remains per logical-run key.
- `CANONICAL_SESSION_USAGE` has one accounting result per session. Its rule is selected from the closed four-CLI registry.
- `CACHE_EFFICIENCY_SIGNAL` distinguishes unavailable, input-only, and measured values; unavailable is not zero.
- A stable `QUERY_RESULT` other than `capture_health` exists only when the input set has zero failures.
- `PARQUET_EXPORT` is derived, attributable, atomic, and rebuildable. It is never authoritative state.
- `INSTALLED_COMPONENT` and `.agent-factory/usage/` have independent lifecycles. Component removal preserves evidence; full Factory removal does not.

## Activity-Graph Orchestration Entities

The activity graph replaces both the linear playbook FSM and the cycle engine as the delivery routing model. Agents declare structured inputs and outputs. The precondition evaluator checks inputs against the repository. Sequence emerges from the dependency chain — no named stages, no transition matrix, no route table.

These entities supersede `DELIVERY_MODEL`, `CYCLE_DECLARATION`, `ROUTE_DECLARATION`, `DELEGATION_GRANT`, and the v1 `WORKSTREAM_STATE` and `SESSION_BINDING`. The superseded entities are removed from the codebase; they remain documented in git history. `VALIDATOR_RESULT` carries forward with the same structure.

Proposal trace: [activity-graph-orchestration.md](../../proposals/activity-graph-orchestration.md)

```mermaid
erDiagram
    AGENT_DEFINITION ||--o{ REQUIRED_INPUT : "inputs.required"
    AGENT_DEFINITION ||--o{ CONTEXT_INPUT : "inputs.context"
    AGENT_DEFINITION ||--|| OUTPUT_SPEC : "outputs"
    OUTPUT_SPEC ||--o{ OUTPUT_DECLARATION : "declarations"
    REQUIRED_INPUT ||--o{ INPUT_CONDITION : "conditions"
    OUTPUT_DECLARATION }o--|| VALIDATOR_RESULT : "validator produces"
    PRECONDITION_EVIDENCE }o--|| AGENT_DEFINITION : "evaluates"
    PRECONDITION_EVIDENCE }o--|| REQUIRED_INPUT : "checks"
    FENCE_EVIDENCE }o--|| OUTPUT_DECLARATION : "validates"
    FENCE_EVIDENCE ||--o{ VALIDATOR_RESULT : "contains"
    WORKSTREAM_STATE }o--o{ SESSION_BINDING : "bound by"
    GOVERNED_ARTIFACT }o--o| WORKSTREAM_STATE : "scoped to"

    AGENT_DEFINITION {
        string name
        string tier "economy | standard | strong"
        object inputs "required and context subkeys"
        object outputs "minimum_changed and declarations"
    }
    REQUIRED_INPUT {
        string artifact "artifact type identifier"
        string path_pattern "glob with {name} placeholders"
        list conditions "nullable — InputCondition list"
    }
    INPUT_CONDITION {
        string field "nullable — frontmatter field name"
        string value "nullable — exact match (with field)"
        list one_of "nullable — any-match list (with field)"
        string check "nullable — trusted validator identifier"
    }
    CONTEXT_INPUT {
        string path "plain path or glob, no conditions"
    }
    OUTPUT_SPEC {
        int minimum_changed "how many declarations must have a match"
    }
    OUTPUT_DECLARATION {
        string path_pattern "glob pattern for output artifacts"
        string validator "trusted validator identifier"
        bool required "true if output must be created or modified"
    }
    PRECONDITION_EVIDENCE {
        string agent_name "evaluated agent"
        string input_artifact "required input reference"
        string status "satisfied | unsatisfied"
        string matched_path "nullable — file that satisfied the input"
        string condition_result "nullable — detail from condition check"
    }
    FENCE_EVIDENCE {
        string session_id "owning session"
        string invocation_id "unique activity invocation"
        string agent_name "agent that ran"
        string aggregate_result "pass | fail"
        int declarations_changed "count of declarations with matches"
        int minimum_required "from output spec"
    }
    VALIDATOR_RESULT {
        string artifact_type "e.g. proposal"
        string artifact_ref "file path or pattern"
        string assessed_commit "40-character SHA"
        list checks "name, passed, detail triples"
        list warnings "free-text strings"
    }
    WORKSTREAM_STATE {
        int schema_version "always 2"
        string workstream_id "filesystem-safe slug"
        string topic "human-readable description"
        string origin_ref "nullable, path to proposal"
    }
    SESSION_BINDING {
        string session_id "CLI session identifier"
        string workstream_id "known identifier or null for Open Stage"
        string bound_at "UTC timestamp, ISO 8601"
    }
    GOVERNED_ARTIFACT {
        string path "canonical tracked path"
        string scope "workstream identifier or global"
        string representation "frontmatter | top-level-yaml | first-line-comment"
    }
```

### Notes

- **AGENT_DEFINITION** is parsed from agent definition files under `packages/factory/agents/` (tracked source) or `.agent-factory/factory/agents/` (installed copy). `inputs.required` and `outputs` determine the agent's position in the precondition graph. `inputs.context` is reading material, not a graph edge. Agent definitions missing `outputs.minimum_changed` or whose declarations omit `path_pattern`, `validator`, or `required` are invalid.
- **REQUIRED_INPUT** declares one artifact the agent needs. A `conditions` list adds constraints checked against YAML frontmatter. An entry with no `conditions` key checks file existence only. Each condition type is mutually exclusive: `field`+`value`, `field`+`one_of`, or `check`.
- **INPUT_CONDITION** with `check` references a trusted validator by name. The engine resolves the name to a bash script under `.agent-factory/factory/scripts/` or a Python validator under `.agent-factory/factory/engine/validators/`. The model never contains shell commands.
- **OUTPUT_DECLARATION** names a `validator` that runs against created or modified files matching `path_pattern` after the activity completes. `required: true` means the fence fails if no match exists. `required: false` means the output is optional — if it changed, its validator runs; if it did not change, it is skipped.
- **PRECONDITION_EVIDENCE** is the evaluator's per-requirement result. One evidence record per required input per agent. The evaluator never writes repository state.
- **FENCE_EVIDENCE** is stored at `.agent-factory/checks/fences/<session-id>/<invocation-id>.yaml`. The aggregate passes only when every required output changed, `declarations_changed >= minimum_required`, and every invoked validator passed. Fence failure does not block human action. For external orchestrators, the fence result determines whether chaining proceeds.
- **VALIDATOR_RESULT** is immutable once produced. Carried forward from the cycle model with the same structure. Every result carries the assessed commit SHA, individual check results, and warnings.
- **WORKSTREAM_STATE** is persisted at `.agent-factory/workstreams/<workstream-id>.yaml`. The file is immutable after creation — no `cycle`, `attempt`, `revision`, `delegation`, or `work` fields. Multiple sessions may bind to the same workstream. No concurrency control is needed because the file does not change.
- **SESSION_BINDING** is persisted at `.agent-factory/workstreams/sessions/<session-id>.yaml`. The `workstream_id` key must always be present: a known identifier means the session is bound, explicit `null` means Open Stage, and a missing key fails validation. Selecting a different workstream updates `workstream_id` and `bound_at`. The binding is session-scoped and dies with the session.
- **GOVERNED_ARTIFACT** is any artifact in the closed first-release set: proposals, epics, stories, Gherkin feature files, `architecture.dsl`, `scope-map.md`, and `entity-model.yaml`. The `scope` field is read from YAML frontmatter when present, otherwise from a `scope:` declaration on the first line of the file. Proposals use `scope` in place of `title`. A lint check at artifact creation time verifies the declaration is present and carries either `global` or a known workstream identifier.
- **Path resolution:** The evaluator resolves a `path_pattern` in four ordered steps: glob expansion (replace placeholders with `*`), scope filtering (keep only candidates whose `scope` matches the bound workstream or equals `global`; skipped in Open Stage), condition checking (evaluate all conditions, remove failing candidates), and cardinality (zero = unsatisfied, one = satisfied, multiple = reported for human selection).
- **No delegation in the engine.** Chaining happens externally — an external orchestrator inspects evaluator evidence after each fence. No delegation grant, attempt counter, or retry limit exists in the engine, agent definitions, or session bindings.
