---
title: Finding File Template
version: 1.0.0
---

# Finding File Template

Skeleton for a single `docs/findings/<TAG>-NNNN.md` file. Governed by [finding-format.md](../conventions/finding-format.md).

## Frontmatter

```markdown
---
id: SPEC-0001
source: spec-review          # the review that produced it (spec-review, atam-review, fagan-review, security-review, reconcile, bug-hunt, grilling)
severity: major              # critical | major | minor  (or the review's own scale, e.g. high|medium|low)
category: defect             # defect | suggestion | question
artifact: docs/spec/prd.md#NFR-01   # file#anchor or path:line the finding is about
status: open                 # open | resolved
traces: [NFR-01]             # requirement / use-case / ADR IDs the finding relates to (optional)
---
```

## Body

```markdown
# <one-line finding title>

**What is wrong:** <the defect, stated concretely>

**Fix:** <the concrete remediation>
```

## Referenced from

- [finding-format.md § Format](../conventions/finding-format.md#format)
