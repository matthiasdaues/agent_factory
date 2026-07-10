---
id: RECON-0005
source: reconcile-spec
severity: minor
category: defect
artifact: factory/playbooks/technical-poc.md#L60,L63
status: open
traces: []
---

# Two anchors in the new technical-poc.md playbook target the wrong GitHub slug for em-dash headings

**What is wrong:** `factory/playbooks/technical-poc.md` (added this range, commit `a6006f9`) links to two headings that use the repo's usual `## Step N — Title` numbering style: `[Pugh Matrix skill § Build the matrix](../skills/pugh-matrix/SKILL.md#step-1-build-the-matrix)` (line 60) and `[write-adr § Check for conflicts](../skills/write-adr/SKILL.md#step-1-check-for-conflicts)` (line 63). The target headings are `## Step 1 — Build the matrix` and `## Step 1 — Check for conflicts`. GitHub's actual heading-slug algorithm (verified directly against the `github-slugger` package, the same one GitHub uses) strips the em dash and collapses the two spaces around it into a double hyphen: `step-1--build-the-matrix` and `step-1--check-for-conflicts` — not the single-hyphen `step-1-build-the-matrix` / `step-1-check-for-conflicts` written in the links. Both links land on the correct file but the wrong spot (the reader is dropped at the top of `SKILL.md` rather than the cited step). This is a new instance of the same anchor-precision class this same reconciliation pass already handled in `factory/rulebooks/conventions/branching-policy.md` (root `RECON-0003`, fixed in commit `87a996d` by deliberately anchoring to a plain, non-numbered heading instead of a `Step N —` one, sidestepping this exact ambiguity) — evidence the project already knows numbered em-dash headings are unsafe anchor targets, but the two new playbooks were not checked against that lesson before commit. No other link in either new playbook is affected: `../agents/implementation-agent.md#branching-model` and `../skills/domain-modeling/SKILL.md#offer-adrs-sparingly` both target plain (non-numbered, no em dash) headings and slugify correctly as written.

**Fix:** Either (a) double the hyphen in both anchors — `#step-1--build-the-matrix` and `#step-1--check-for-conflicts` — or (b), consistent with how `RECON-0003` (root) was actually fixed, retarget both links at the nearest stable non-numbered heading in each file (e.g. anchor `pugh-matrix/SKILL.md` at its top-level `## Step 1 — Build the matrix` parent section only if one exists, otherwise keep the double-hyphen form). After fixing, spot-check any other `Step N —`-anchored link added in future playbooks the same way — `cross-reference-format.md` is not mechanically gate-checked, so this class of error will not be caught by any lint.
