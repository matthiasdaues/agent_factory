[back to index](README.md)

# 2. Architecture Constraints

Constraints are fixed decisions the architecture must respect. They come from the PRD (§6 Constraints, §2 Non-Goals) and the workflow the orchestrator serves.

## 2.1 Technical Constraints

| ID   | Constraint                                                                                                                                                                  | Source                 | Consequence for the architecture                                                                                                                                            |
| ---- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| TC-1 | Implementation language is **Python 3.10+** (for modern typing).                                                                                                            | C1                     | Ports expressed as `typing.Protocol`/ABC; dataclasses for entities.                                                                                                         |
| TC-2 | The host is a **git repository with `pre-commit`** installed and configured.                                                                                                | C2                     | The gate is realized as a commit whose hooks run; no bespoke check runner.                                                                                                  |
| TC-3 | **GitHub Copilot CLI** is installed and authenticated for the MVP.                                                                                                          | C3                     | Copilot is the first concrete `CLIAdapter`; auth failure is a first-class halt.                                                                                             |
| TC-4 | Each target CLI offers a **non-interactive ("headless")** mode; exact flags differ per CLI.                                                                                 | C4, T-01               | CLI-specific flags are confined to adapters, never the core.                                                                                                                |
| TC-5 | **Reuse `agents/`, `skills/`, `scripts/` as-is**, resolved from the package-relative path, exposed in target projects via symlinks (ADR-0010).                              | C5, NG1                | The orchestrator *drives* these assets; it must not re-implement agent or skill behaviour.                                                                                  |
| TC-6 | Project home is **`orchestrator/`**; installed globally via `uv tool install`.                                                                                              | C6, T-07, ADR-0010     | `orchestrate` is a global CLI command; agent/skill/script paths are resolved relative to the package.                                                                       |
| TC-7 | **Prefer the Python standard library** (`argparse`); justify every third-party dependency.                                                                                  | NFR-7, T-06            | `jsonschema` is the sole anticipated runtime dependency (schema validation); see [ADR-0006](adr/0006-stdlib-first-dependency-policy.md).                                    |
| TC-8 | **`uv` is the environment, packaging, and distribution tool**: `pyproject.toml` + committed `uv.lock`; managed Python 3.10+; `orchestrate` installed via `uv tool install`. | NFR-5, NFR-1, ADR-0007 | Build/dev tooling — *complementary* to TC-7, not a runtime dependency. Gate/dev tools (`pre-commit`, `ruff`, `pytest`) live in a uv dev group, outside the runtime surface. |

## 2.2 Organizational and Process Constraints

| ID   | Constraint                                                                                                                               | Source        | Consequence                                                                                                                    |
| ---- | ---------------------------------------------------------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| OC-1 | **Session isolation is non-negotiable**: no agent invocation may inherit another's conversation context.                                 | NFR-2, BR-004 | Isolation is achieved by process boundary — a fresh subprocess — not by prompt discipline.                                     |
| OC-2 | **Human judgement is reserved for phase gates.**                                                                                         | G5, FR-G      | The orchestrator runs autonomously *within* a phase and stops *at* phase boundaries.                                           |
| OC-3 | **Fail safe over fail fast on ambiguity**: on cap exhaustion, gate error, adapter-auth failure, or rejection, halt and summon the human. | G7, NFR-3     | `Halted` is a designed terminal state, distinct from `Complete`.                                                               |
| OC-4 | The orchestrator is **not a CI system and not a ticket tracker** in this version.                                                        | NG2, NG3      | No GitHub Issues/Jira integration; findings live in a local store whose schema maps cleanly to a future ticket adapter (T-04). |
| OC-5 | **CLI only — no GUI.**                                                                                                                   | NG4           | The only human interface is the terminal (argparse commands + interactive approval prompt).                                    |

## 2.3 Conventions

- **arc42** for architecture documentation; **C4 / Structurizr DSL** for models; **ADR according to Nygard** with a **Pugh Matrix** for decisions.
- **Clean Architecture**: the core depends inward on abstractions (ports); concretions (adapters) depend outward on the core. No core module imports a concrete CLI, filesystem layout, or git command.
- Severity casing is **lowercase everywhere** (`error`/`warning`/`info`), matching `spec-lint` output and BR-002.
- All persisted state (`run.json`, finding files) is written **atomically** (write-then-rename).
