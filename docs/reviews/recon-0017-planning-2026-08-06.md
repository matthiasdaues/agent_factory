---
title: Planning Pass — RECON-0017 Pre-push Test Gate
category: planning
source: RECON-0017
date: 2026-08-06
version: 1.0.0
---

# Planning Pass — RECON-0017 (pre-push full-suite test gate)

Planning the implementation of open defect RECON-0017 into the local backlog.
This is a planning pass, not a review: it files exactly one backlog story that
fixes the defect and references the existing finding. No new finding is filed
(RECON-0017 is the originating defect reference); no duplicate is created.

## Finding table

| Finding                                                                         | Artifact                              | Category | Severity |
| ------------------------------------------------------------------------------- | ------------------------------------- | -------- | -------- |
| RECON-0017 — pre-push full-suite test gate is documented but never wired (open) | factory/config/pre-commit-config.yaml | Defect   | Major    |

RECON-0017 is **open** and addressed by the filed story; it remains open until
implementation verifies the hook is present and docs/config agree.

## Defect summary

ADR-0003 (accepted, unsuperseded) and `factory/README.md` § "Test execution
hooks" both document a pre-push hook that runs `factory/scripts/run-tests --full`
and blocks `git push` on failure — point 2 of the three-point test regime. The
canonical config that `init-factory` splices into consumer projects
(`factory/config/pre-commit-config.yaml`) defines no `pre-push`-stage hook and
no `run-tests` entry at all. ADR-0003 is the intended truth; the configuration
drifted. Work can currently leave the local machine with a failing full suite.

Confirmed against the repo: `grep run-tests factory/config/pre-commit-config.yaml`
returns nothing; this repo's own `.pre-commit-config.yaml` has only the
pre-commit `run-tests --changed-only` hook; no `stages: [pre-push]` entry
exists anywhere. An orphan `.github/hooks/pre-push` script exists on disk but
is untracked, not installed into `.git/hooks/`, and not carried to consumers —
it is not the live mechanism the README describes.

## Planned fix (one story)

**ST-0073 — Wire pre-push full-suite test gate into canonical pre-commit
config** (`backlog/ST-0073.md`, epic: Test Execution Hooks, tier: economy,
status: pending).

- Add `agent_factory_hook-run-tests-full` to the existing `- repo: local`
  block in `factory/config/pre-commit-config.yaml` with `entry: factory/scripts/run-tests --full`, `stages: [pre-push]`, `pass_filenames: false`, `always_run: true`.
- `merge-precommit-config` carries it into consumer projects automatically
  (it splices the whole block keyed on the template's first hook id) — no
  script change required.
- Add an `init-factory` test asserting the spliced consumer config contains
  the pre-push hook.
- Confirm `factory/README.md`'s three-point test-regime description matches what
  is installed; resolve or file any residual drift in point 1 (pre-commit
  `--changed-only`, also absent from the canonical config) rather than leave it
  silent.

**Traces:** UC-09 (extensions 1c, 5a; BR-026), ADR-0003, RECON-0017.
**Deps:** ST-0009 (`run-tests` script, done). Supersedes the abandoned raw-hook
approach in ST-0013 (pending, unbuilt).

## Scope discipline (YAGNI)

- One story, one defect. RECON-0017 scopes its fix to the pre-push full-suite
  gate; the story does the same.
- The adjacent pre-commit `--changed-only` drift (README point 1) is flagged in
  the story's investigation notes as a possible follow-up, not silently
  bundled. The story's README consistency criterion requires that drift to be
  either closed in-change or filed separately.
- No specification or architecture change is needed: ADR-0003 is accepted and
  unsuperseded; the README correctly restates it. Implementation brings the
  config into conformance with the documented truth.

## Validation

- `backlog-lint --backlog-dir backlog` reports 0 errors across 73 story files
  (2 informational VR-028 warnings: ST-0013 and ST-0073 each list output paths
  that already exist, expected for stories that modify existing files).
- `mdformat --number backlog/ST-0073.md` produces no formatting diff.

## Disposition

Planning complete. One backlog story filed referencing the existing open
finding RECON-0017. The defect remains open until ST-0073 is implemented and the
hook is verified present with docs/config in agreement.

## Artifacts

- `backlog/ST-0073.md` — the implementation story (canonical backlog artifact).
- `docs/reviews/recon-0017-planning-2026-08-06.md` — this report.
- `docs/findings/RECON-0017.md` — originating defect (referenced, not modified).
