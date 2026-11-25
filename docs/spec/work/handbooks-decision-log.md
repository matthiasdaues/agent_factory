# Decision Log: Factory Handbooks Run

This log records every decision taken while the
[Factory Handbooks proposal](../../proposals/factory-handbooks.md) runs through
the feature-addition playbook on `feature/handbooks`. "Run lead" is the Claude
Code session that drives the run. "Product owner" is the stakeholder. A row is
added when a decision is made and is never deleted.

| ID   | Date       | Decided by    | Decision                                                                                                                                                       | Reason                                                                                                                                               |
| ---- | ---------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| L-01 | 2026-11-25 | product owner | The run works on `feature/handbooks`, cut from `dev` at the acceptance commit `4ebf5101f70c1540a0d53dcfb3d00cfa977d361a`, which is also the planning baseline. | The product owner asked for a feature branch in its own worktree.                                                                                    |
| L-02 | 2026-11-25 | run lead      | The feature branch's worktree is `.current-work/feature/handbooks/invocation`.                                                                                 | `dispatch init` uses that path for a feature branch, so story worktrees under `.current-work/feature/handbooks/` sit next to it, not inside it.      |
| L-03 | 2026-11-25 | product owner | The specification and the backlog are written on `feature/handbooks`, not on `dev`.                                                                            | The product owner asked to run the whole feature in the worktree. The branching policy allows indexed artifacts on any branch.                       |
| L-04 | 2026-11-25 | product owner | Every review runs in a Codex session on `gpt-6.2-sol`. When the Codex session limit is reached, the review runs in a fresh Claude Code session on Sonnet 5.5.  | The product owner's instruction for this run.                                                                                                        |
| L-05 | 2026-11-25 | product owner | The run lead decides on its own and asks the product owner only when a decision needs the product owner to settle an ambiguity.                                | The product owner's instruction for this run.                                                                                                        |
| L-06 | 2026-11-25 | run lead      | Specification work is needed; architecture work is not.                                                                                                        | The design adds two gates and changes the newcomer onboarding and an external contract (playbook Step 0.3). `impact.architecture_change` is `false`. |
