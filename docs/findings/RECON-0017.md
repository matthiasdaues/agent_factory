---
id: RECON-0017
source: reconcile
severity: major
category: defect
artifact: factory/config/pre-commit-config.yaml
status: resolved
traces: [UC-09, ADR-0003]
---

# Pre-push full-suite test gate is documented but never wired

**Resolution:** ST-0073 added `agent_factory_hook-run-tests-full` to the
canonical pre-commit configuration and covered fresh installation, merge, and
idempotence. `init-factory` now explicitly installs both the `pre-commit` and
`pre-push` Git hook types, so the configured stage actually fires. The
implementation pass also corrected the prior claim that a client-side pre-push
hook has no bypass: human operators can use `git push --no-verify`; managed
agents remain subject to Factory guardrails.

**What is wrong:** ADR-0003 (status: accepted, unsuperseded) and
`factory/README.md` § "Test execution hooks" both document a pre-push hook that
runs `run-tests --full` and blocks `git push` when tests fail. ADR-0003 calls
it the "ready-to-share gate — full suite, unavoidable, blocks work leaving
local machine," and the README lists it as point 2 of the three-point test
regime: "Pre-push hook (no bypass) — runs full test suite before sharing your
work, blocks push if tests fail."

Neither hook configuration implements it:

- `factory/config/pre-commit-config.yaml` — the canonical config
  `init-factory` splices into consumer projects — defines no `pre-push`-stage
  hook and no `run-tests --full` entry. It has no test hook at all.
- This repo's own `.pre-commit-config.yaml` has a single test hook,
  `run-tests --changed-only`, on the `pre-commit` stage, scoped to
  `^(src/|tests?/)`. No `stages: [pre-push]` entry exists anywhere; a `git log -S pre-push -- factory/config/pre-commit-config.yaml` search returns
  nothing — the hook was never added.

The only full-suite enforcement that exists is the FSM `tests_pass`
entry condition (`factory/scripts/run-tests --full`) evaluated by
`phase advance` before PHASE_4_GATE and PHASE_5_QUALITY. That is a phase-gate
mechanism, not a git-push gate, so it only applies to playbook-driven runs and
does not stop a developer pushing broken tests outside the harness.

Net: the documented pre-push gate is unimplemented, so work can leave the local
machine with a failing full test suite.

**Fix:** Wire the pre-push gate ADR-0003 specifies. Add a `pre-push`-stage
hook to `factory/config/pre-commit-config.yaml` (id prefixed
`agent_factory_hook-`) that runs `factory/scripts/run-tests --full`, and ensure
`init-factory` / `merge-precommit-config` carry it into consumer projects
alongside the existing hooks. Then confirm the README's three-point description
matches what is actually installed. Filed as a code defect rather than a doc
correction because ADR-0003 is accepted and unsuperseded — it is the intended
truth, and `factory/README.md` correctly restates it; the configuration is what
drifted. (Resolved when the hook is present and the docs/config agree.)
