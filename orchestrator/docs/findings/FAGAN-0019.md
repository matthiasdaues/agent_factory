---
id: FAGAN-0019
source: fagan-review
severity: major
category: defect
artifact: src/orchestrator/adapters/backlog_store.py#get_story
status: resolved
traces: [VR-022]
---

# Path traversal via crafted story_id

**What is wrong:** `story_id` is interpolated directly into a file path (`backlog_dir / f"{story_id}.md"`). A crafted ID like `../docs/spec/prd` could escape the backlog directory and read or write sibling markdown files. While the attack surface is limited (only the operator interacts), it's a defence-in-depth gap.

**Fix:** Validate `story_id` against `^ST-[0-9]{4,}$` before path construction, and verify the resolved path stays under `backlog_dir`.
