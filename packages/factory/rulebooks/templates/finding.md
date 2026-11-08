---
title: Finding File Template
version: 2.0.0
---

# Finding File Template

Skeleton for a single `docs/findings/<TAG>-NNNN.md` file. Governed by [finding-format.md](../conventions/finding-format.md). Only a `critical` or `major` finding of the category `defect` or `risk` gets a finding file. A `minor` finding becomes a register file instead, as [finding-format.md § Register files](../conventions/finding-format.md#register-files) describes.

## Frontmatter

```markdown
---
id: FAGAN-0042
source: fagan-review         # the review or session that found it (spec-review, atam-review, fagan-review, security-review, reconcile, bug-hunt, grilling, diagnosis)
review_class: code           # document | code | security | architecture | runtime
category: defect             # defect | risk | suggestion
type: function               # a type from the vocabulary of the class
severity: major              # critical | major, computed from basis
basis:                       # the shape of the class, as docs/spec/schemas/finding-basis.json defines it
  in_use: false              # document, code, runtime: in_use, harms_downstream, fails_purpose, raises_cost
  harms_downstream: false    # security: effect, second_breach, trusted_access, non_default, user_action, confidence, in_use
  fails_purpose: true        # architecture: importance, exposure, in_use
  raises_cost: false
rating:                      # Critical | High | Medium | Low for a security finding; null in every other class
override_by:                 # human field, null when written by an agent
override_reason:             # human field, null when written by an agent
stop_confirmed_by:           # human field, null when written by an agent
stop_confirmed_reason:       # human field, null when written by an agent
artifact: packages/factory/scripts/premerge-check:120   # path:line, path:start-end, or path#anchor
status: open                 # open | resolved | deferred | waived
owner: developer-agent       # the agent that acts on the finding next (default: producer of the artifact)
traces: [ST-0351]            # requirement / use-case / ADR IDs the finding relates to (optional)
---
```

The four human fields are `null` in every finding that an agent writes. No agent changes them later.

Status values:

- `open` and `resolved`: set by an agent.
- `waived`: set by the stakeholder only.
- `deferred`: set by the migration only, on a file without `review_class`.

## Body

```markdown
# <one-line finding title>

**What is wrong:** <the defect, stated concretely>

**Why this severity:** <one sentence per "yes" answer, per precondition, or for the effect class; names the evidence for in_use>

**Fix:** <the concrete remediation>
```

A `critical` finding ends with this section. No other severity holds it.

```markdown
## Possible damage

- <one thing outside the artifact that depends on it, as a fact from git or the file tree> — check: <one command or step the stakeholder runs>
```

In a `critical` finding, the first sentence of the `**Why this severity:**` line names the evidence for `in_use`, because the stop notice prints that sentence.

## Referenced from

- [finding-format.md § Format](../conventions/finding-format.md#format)
