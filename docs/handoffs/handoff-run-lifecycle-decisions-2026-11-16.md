## Resume point (2026-11-18)

Proposal accepted at c880ec6497e0b4c6fbc82241575beeefd0b12d33. Spec commits on `dev`: ae806697, 48faee8b, 281d19d7 (requirements), c650300a (QA strategy), b5f2c72a, 67c26aa7 (domain files). A requirements fix pass for RL-G17 to RL-G21 and OI-02 to OI-11 was still running at the break; check `git log` for its commit.

Open for the stakeholder: (1) on the last tier only the implementation agent caps `re-dispatch`, since `dispatch` cannot tell the human fixed the cause; (2) whether `crap-score` and `mutation-testing` also read the old underscore keys; (3) the domain-modeling agent also renamed `test_design_verify` to `test-design-verify`.

Next: test-strategy agent checks the QA strategy against the new contracts, then spec-review-agent, module-graph-check, architecture-agent, architecture review, planning-agent, backlog-lint. Stop before the implementation agent.

Update: the requirements fix pass stopped before its commit. Its edits are uncommitted on `dev` in `docs/spec/features/run-lifecycle.feature` (132 Scenarios), `docs/spec/areas/mechanized-dispatch.md` and `docs/spec/work/run-lifecycle-gaps.md`. Still to run: `validate`, then commit those three files with an explicit pathspec. It adds RL-G22 (how `re-dispatch` tells the RL-G19 case from a refused retry; recommendation: grant new attempts when the unit can no longer escalate) and RL-G23 (same as open point 2 above).
