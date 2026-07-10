---
id: FAGAN-0021
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/backlog_store.py#_parse_frontmatter
status: resolved
traces: [VR-022]
---

# Frontmatter not schema-validated

**What is wrong:** Story frontmatter is parsed by a hand-rolled parser that only supports a subset of YAML and is not validated against the published `StoryFrontmatter` JSON schema. Unknown/missing fields or valid-but-richer YAML (nested structures, anchors) can be silently misparsed.

**Fix:** Parse YAML with a proper parser and validate against the published schema before returning a `Story` object. This is consistent with how `findings_store.py` validates against its schema.
