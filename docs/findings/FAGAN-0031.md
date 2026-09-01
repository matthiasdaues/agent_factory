---
id: FAGAN-0031
source: fagan-review
severity: major
category: defect
artifact: factory/scripts/crap-score:91-133
status: resolved
traces: [test-design.feature/Rule-15]
---

# crap-score threshold search leaks across YAML sections

**What is wrong:** The `read_threshold_from_testing_yaml` function uses a regex
chain to find `gates:` then `crap_score:` then `threshold:`, but the third search
is unbounded — it searches all text after `crap_score:`, not just the `crap_score`
subsection. If a sibling gate section (e.g. `mutation_testing:`) defines its own
`threshold:` key and `crap_score` lacks one, the function returns the wrong
threshold instead of `None`. The gate would then silently apply a foreign
threshold value, and `resolve_threshold` would not fall through to the hardcoded
default.

Reproduction: add `threshold: 50` under `mutation_testing:` in `testing.yaml`
and remove `threshold:` from `crap_score:`. The function returns 50.0 instead of
None.

**Fix:** After extracting the `crap_score:` position, limit the threshold search
to the text between `crap_score:` and the next peer-level key. The simplest
approach is to find the next line at the same indentation level as `crap_score:`
(a line matching `^\s{2}\w+:` that is not deeper-indented content) and truncate
the remaining text there before searching for `threshold:`.
