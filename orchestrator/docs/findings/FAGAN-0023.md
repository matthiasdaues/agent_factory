---
id: FAGAN-0023
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/agent_registry.py#_parse_list_field
status: resolved
traces: [VR-011]
---

# Malformed frontmatter yields empty outputs silently

**What is wrong:** If an agent definition's frontmatter is malformed, `_parse_list_field()` returns an empty list. The phase proceeds with no declared outputs, meaning the gate stages nothing (empty commit) and completion checks are vacuous. This degrades silently instead of failing fast as VR-011 requires.

**Fix:** Parse frontmatter with a proper YAML parser and validate that required fields (`outputs`) are present and non-empty. Raise on malformed agent definitions.
