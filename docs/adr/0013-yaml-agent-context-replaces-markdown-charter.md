---
id: "0013"
status: proposed
evaluation: pugh-matrix
---

# YAML agent context replaces markdown charter

## Context

The project charter (`docs/charter/`) was the interface contract between factory agents and a project's self-determined practices. The charter used three markdown files (`tech-stack.md`, `development.md`, `house-rules.md`) with heading-delimited sections.

Two problems surfaced in production use:

1. **Staleness.** As projects mature, charter content duplicates decisions already captured in a developer handbook, ADRs, and convention files. The charter becomes a second source of truth that drifts from the real one.

2. **Fragile parsing.** Agents parse charter fields by heading regex, not by key. Placeholder detection relies on string matching ("To be decided") rather than mechanical null detection. Per-field `source:` pointers to authoritative documents are awkward to express in markdown without inventing ad-hoc notation.

The `testing.yaml` file already demonstrated a YAML-based pattern that works: machine-readable, directly parseable, consumed by scripts and hooks without heading-regex fragility.

Three format alternatives were considered: keep the existing markdown charter (baseline), move to YAML, or move to JSON.

## Decision

Replace `docs/charter/` with `docs/agent-context/` using YAML files. Three index files (`stack.yaml`, `workflow.yaml`, `governance.yaml`) replace the three markdown charter files. A fourth file (`reading-guides.yaml`) provides concern-based routing into the index files. `testing.yaml` continues as a lifecycle-exempt peer.

| Criterion                       | Weight | Markdown (baseline) | YAML    | JSON   |
| ------------------------------- | ------ | ------------------- | ------- | ------ |
| Machine parseability            | 3      | 0                   | +1      | +1     |
| Staleness resistance            | 3      | 0                   | +1      | +1     |
| Human readability / editability | 2      | 0                   | 0       | -1     |
| Per-field source pointers       | 3      | 0                   | +1      | +1     |
| Consistency with testing.yaml   | 1      | 0                   | +1      | 0      |
| Backward compatibility          | 2      | 0                   | 0       | -1     |
| **Weighted total**              |        | **0**               | **+10** | **+5** |

YAML dominates on every criterion that matters (+10 vs. JSON's +5). JSON ties on machine concerns but loses on human editability and backward compatibility (the factory ecosystem already uses YAML for structured config, not JSON). Markdown loses on the three highest-weighted criteria.

Format detection provides backward compatibility: factory consumers walk a three-step chain (`docs/agent-context/stack.yaml` then `docs/charter/tech-stack.yaml` then `docs/charter/tech-stack.md`) and select the appropriate validation mode. Legacy markdown charter projects continue to work unchanged.

A new `context-lint` script (replacing `charter-lint`) validates the YAML structure with `CX-*` finding codes, enforcing key presence, mode compliance, source-pointer integrity, and reading-guide reference resolution.

## Consequences

**Easier:**

- Agents parse context fields by YAML key, not heading regex. Placeholder detection is mechanical (`null` vs. a value).
- Per-field `source:` pointers to authoritative project documents are first-class YAML structure, enabling the downstream-index pattern that prevents staleness.
- `context-lint` validation is structural rather than string-based, covering key presence, mode compliance, source-pointer resolution, and reading-guide reference integrity.

**Harder:**

- Every factory consumer that reads charter files must be updated with format detection and new paths. The proposal's consumer inventory lists approximately 40 affected artifacts across agents, skills, playbooks, scripts, hooks, and templates.
- Legacy markdown charter projects remain supported but frozen. New features target YAML only.
- Human operators accustomed to editing markdown must learn the YAML schema. The schema is intentionally minimal: flat keys, `null` placeholders, `name`/`source` pairs.
