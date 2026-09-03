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
        int    phase "nullable"
        string phase_name "nullable"
        string tier "nullable — economy | standard | strong"
        string description
        string path
        int    tokens "tiktoken cl100k_base body count"
        int    total_tokens "body + skills + rulebooks"
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
        string source "docs/charter/testing.yaml gates section"
    }
    GATE_ENTRY {
        string name "crap_score | mutation_testing | test_design_verify"
        bool enabled "true | false"
        float threshold "nullable — gate-specific"
    }
```

### Notes

- **RISK_CLASS** has three Factory convention defaults (`critical`, `standard`, `structural`). Projects may add custom classes in `docs/charter/testing.yaml`'s `risk_classes:` section. Precedence: `testing.yaml` inline > project-linked strategy document > Factory convention defaults.
- **TEST_DESIGN_SECTION** is a markdown section (`#### Test Design`) within a story's building-block entry in `backlog/epics.md`. It is carried verbatim into the corresponding `backlog/ST-NNNN.md` by `create-backlog-stories`.
- **PRIOR_TESTS_SECTION** is a markdown section (`#### Prior Tests`) for non-owning stories. The developer-agent runs these tests first and must keep them green.
- **WAIVER** is a blockquote line within the `#### Test Design` section: `> Waiver: DOM-01 — owned by tests/test_domain.py::test_entity_uniqueness`. The `test-design-verify` gate parses these and validates the named test module exists.
- **GATE_CONFIG** is a new section in `docs/charter/testing.yaml` that centralizes gate configuration. It does not define gate execution ordering — [ADR-0012](../../adr/0012-dispatcher-owned-semantic-gate-loop.md) owns the dispatcher's gate sequence.
- **GATE_ENTRY** configures an individual gate. `test_design_verify` is implicitly enabled when test-design output exists in the story and skipped otherwise.

## Agent Context Entities

The agent context is the factory-facing interface to project knowledge. It replaces the charter as the structured contract between factory agents and the project's self-determined practices. The two-layer architecture (reading guide over index files) and two-mode lifecycle (primary then index) are modeled below.

```mermaid
erDiagram
    READING_GUIDE ||--o{ CONCERN_ENTRY : "routes by concern"
    CONCERN_ENTRY ||--o{ KEY_PATH_REFERENCE : "lists"
    KEY_PATH_REFERENCE }o--|| INDEX_FILE : "points into"
    INDEX_FILE ||--o{ INDEX_FIELD : "declares"
    INDEX_FILE ||--|| MODE_STATE : "has"
    INDEX_FIELD ||--o| DEFERRED_MARKER : "may carry"
    INDEX_FIELD ||--o| SOURCE_POINTER : "may carry"
    CX_FINDING }o--|| INDEX_FILE : "reported against"
    CX_FINDING }o--o| READING_GUIDE : "reported against"
    TESTING_YAML }o--o| CX_FINDING : "CX-PARSE only"
    FORMAT_DETECTION ||--o| INDEX_FILE : "selects"

    READING_GUIDE {
        string path "docs/agent-context/reading-guides.yaml"
        string role "Layer 1 — concern-based routing"
    }
    CONCERN_ENTRY {
        string concern "e.g. backend, frontend, testing"
        list references "key-path notation strings"
    }
    KEY_PATH_REFERENCE {
        string file "e.g. stack.yaml"
        string key_path "nullable — dotted path e.g. frameworks.backend"
    }
    INDEX_FILE {
        string name "stack.yaml | workflow.yaml | governance.yaml"
        string path "docs/agent-context/<name>"
        string mode "primary | index"
    }
    INDEX_FIELD {
        string key "dotted key path within the index file"
        string value "nullable — inline value when mode is primary"
        string name "nullable — lookup name when mode is index"
        string source "nullable — path to authoritative document"
    }
    MODE_STATE {
        string mode "primary | index"
    }
    DEFERRED_MARKER {
        string reason "human-readable deferral reason"
    }
    SOURCE_POINTER {
        string path "relative path to authoritative project document"
    }
    TESTING_YAML {
        string path "docs/agent-context/testing.yaml or docs/charter/testing.yaml"
        string role "peer file — machine-readable test config, no lifecycle"
        string writer "detect-test-regime (sole owner)"
    }
    FORMAT_DETECTION {
        string result "yaml-agent-context | legacy-yaml-charter | legacy-markdown-charter | CX-FORMAT error"
    }
    CX_FINDING {
        string code "CX-FILE | CX-PARSE | CX-KEYS | CX-NULL | CX-MODE | CX-SRC | CX-SRC-EXIST | CX-SRC-STALE | CX-GUIDE-REF | CX-FORMAT"
        string severity "error | warning | info"
        string message "human-readable finding text"
    }
```

### Notes

- **READING_GUIDE** is Layer 1 of the agent context. It routes by work-type concern (backend, frontend, testing, architecture, packaging, and project-specific additions) to sections in the Layer 2 index files. It carries no `source:` pointers — only key-path references. It does not participate in the two-mode lifecycle. It is absent in greenfield projects until the first `source:` pointer is written.
- **KEY_PATH_REFERENCE** uses the notation `<file>#<dotted.key.path>` (e.g. `stack.yaml#frameworks.backend`). A bare file reference (`stack.yaml`) means the entire file. `context-lint` validates these references via `CX-GUIDE-REF` by confirming the key path exists in the target file's YAML structure — key existence only, not value content.
- **INDEX_FILE** is one of the three Layer 2 files (`stack.yaml`, `workflow.yaml`, `governance.yaml`). Each covers a distinct domain of project knowledge. They carry `source:` pointers to authoritative project documents and participate in the two-mode lifecycle.
- **INDEX_FIELD** has different shapes depending on mode. In `mode: primary`, a field may be a scalar value, `null`, or a `deferred:` mapping. In `mode: index`, a field carries `name:` and `source:` together. The `deferred:` mapping replaces the entire field value — `deferred` is the sole key; any coexisting `name`/`source` key is a `CX-KEYS` error.
- **MODE_STATE** is one of `primary` (greenfield — index files are the upstream source) or `index` (mature — index files are downstream routing tables). The transition from `primary` to `index` is one-directional and atomic across all three index files. See [state-machines.md](state-machines.md).
- **TESTING_YAML** is a peer file outside the two-mode lifecycle. It is written by `detect-test-regime`, not by `update-context`. `context-lint` validates it with `CX-PARSE` only — no `CX-SRC`, `CX-MODE`, or `CX-NULL` checks apply. Format detection resolves its path independently: `docs/agent-context/testing.yaml` first, `docs/charter/testing.yaml` as fallback, with no `CX-FORMAT` error for the split location.
- **FORMAT_DETECTION** is a shared subfunction used by all factory consumers. It walks a three-step chain: `docs/agent-context/stack.yaml` → `docs/charter/tech-stack.yaml` → `docs/charter/tech-stack.md`. Files in more than one location produce a `CX-FORMAT` error. `testing.yaml` is resolved independently and does not trigger mixed-location errors.
- **CX_FINDING** replaces the charter-lint `CH-*` codes for YAML agent-context validation. Legacy markdown charter projects continue to use the existing `CH-*` codes.

## Referenced from

- [actor-goal-list.md](../../~archive/spec/actor-goal-list.md)
- [UC-01](../../~archive/spec/use_cases/UC-01-advance-a-playbook-phase.md)
- [test-design.feature](../test-design.feature)
- [agent-context.feature](../agent-context.feature)
