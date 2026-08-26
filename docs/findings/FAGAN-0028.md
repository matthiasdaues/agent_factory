# FAGAN-0028 — Suggest Tier Nested Conditionals

**Date:** 2026-08-26  
**Severity:** Trivial  
**Category:** Maintainability  
**Status:** Improvement opportunity

---

## Summary

`suggest_tier()` in `dispatch_lib.py` uses 6 nested conditionals to implement the first-match-wins rubric. The logic is correct but could be extracted for better readability.

## Evidence

```python
# factory/scripts/dispatch_lib.py:1137
def suggest_tier(story_frontmatter: dict[str, Any], project_config: dict[str, Any]) -> str:
    risk_domains = story_frontmatter.get("risk_domains") or []
    if any(d in _STRONG_RISK_DOMAINS for d in risk_domains):
        return "strong"
    
    outputs = story_frontmatter.get("outputs") or []
    safety_critical_paths = project_config.get("safety_critical_paths") or []
    if safety_critical_paths:
        for output in outputs:
            for pattern in safety_critical_paths:
                if fnmatch.fnmatch(output, pattern):
                    return "strong"
    
    top_dirs = set()
    for output in outputs:
        parts = Path(output).parts
        top_dirs.add(parts[0] if parts else output)
    
    if len(top_dirs) >= 2:
        return "standard"
    
    deps = story_frontmatter.get("deps") or []
    if len(deps) >= 3:
        return "standard"
    
    tests = story_frontmatter.get("tests") or []
    if len(top_dirs) <= 1 and tests:
        return "economy"
    
    return "standard"
```

## Specification Alignment

The logic matches the spec's 6-rule rubric exactly.

## Improvement Opportunity

Consider extracting rules into a list of functions or a table for better maintainability:

```python
RULES = [
    ("risk_domains include security/privacy/data_integrity", lambda fm: ...),
    ("outputs match safety_critical_paths", lambda fm, cfg: ...),
    # ...
]
```

## Recommendation

Low priority. The current implementation is correct and well-tested. Refactoring would improve readability but isn't necessary for correctness.