# Internal Inventory: Where Ideas And Decisions Live Today

Investigator A. Snapshot of the repository on branch `dev`, 2026-11-17. Every claim below comes from a file read or a shell count in this task. No external claim appears, so no URL is cited.

## The short answer

The factory records decisions well once a proposal exists, and badly before and around it. Three findings matter most.

1. A proposal carries its decisions in an Appendix table, but the table's "Raised by" cell is free text. It does not link to a transcript, a handoff, or a message. Provenance stops at a phrase such as "draft conversation".
2. Only two outcomes have a vocabulary: accepted and superseded. "Won't do" and "rejected" have no status anywhere. "Deferred" lives in prose lists with no ID and no status.
3. Ideas and decisions that come out of chat sessions land in handoffs, the gitignored scratchpad, or nowhere. The run-lifecycle proposal shows it: twenty decisions sit in an untracked handoff and the proposal itself says "Open Questions: None."

## 1. Artifact types that hold an idea, a decision, or a deferral

| Artifact                 | Path pattern                                                                                  | ID scheme                                                                                  | Status values                                                                                                                           | Writer                                                                         |
| ------------------------ | --------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------ |
| Proposal                 | `docs/proposals/<name>.md`, plus `implemented/` and `superseded/`                             | None. The file name is the key. Rows inside use `DEC-NN` and `PROP-NN`, numbered per file. | `draft`, `open`, `accepted`, `implemented`, `cancelled`, `superseded` (`packages/factory/rulebooks/templates/proposal.md`, Frontmatter) | Stakeholder with VIRGIL and the `draft-proposal` skill; reviewers add findings |
| Proposal Decisions table | Appendix of each proposal                                                                     | `DEC-NN` per file                                                                          | Kind: `decision` or `assumption`                                                                                                        | The author, "written when it is made" (template, Appendix)                     |
| Proposal review findings | Appendix of each proposal                                                                     | `PROP-NN` per file                                                                         | `open`, `fixed`, `resolved`, `waived`                                                                                                   | `proposal-review-agent`; only the stakeholder sets `waived`                    |
| ADR                      | `docs/adr/NNNN-<slug>.md`                                                                     | `ADR` prefix from `next-id` (`rulebooks/conventions/id-prefixes.md`)                       | `accepted`, `proposed`, `superseded by ADR-NNNN`                                                                                        | Architecture agent via the `write-adr` skill                                   |
| Finding                  | `docs/findings/<PREFIX>-NNNN.md`, plus `docs/findings/register/<class>/*.json` for minor ones | `BUG`, `SPEC`, `FAGAN`, `SEC`, `RECON`, `ATAM`, `IMPL`, shared counter                     | `open`, `fixed`, `resolved`, `deferred`; severity `critical`, `major`, `minor`, `note`                                                  | Review agents; rules in `rulebooks/conventions/finding-classification.md`      |
| Todo entry               | `docs/spec/work/todo.md`                                                                      | `T-NNNN` from `next-id T` (`rulebooks/conventions/todo-format.md`)                         | `open`, `resolved`                                                                                                                      | Any agent that defers a decision or a question                                 |
| Term candidate           | `docs/spec/work/term-candidates.md`                                                           | None; keyed by term                                                                        | A Status column, no values defined                                                                                                      | Grilling and `reverse-map`                                                     |
| Backlog story            | `backlog/ST-NNNN.md`                                                                          | `ST`                                                                                       | Story lifecycle, outside this inventory                                                                                                 | Planning agent                                                                 |
| Handoff                  | `docs/handoffs/handoff-<topic>-<date>.md`                                                     | None                                                                                       | None                                                                                                                                    | The outgoing agent (`rulebooks/conventions/handoff-format.md`)                 |
| Review report            | `docs/reviews/<kind>-<date>-<topic>.md`                                                       | None                                                                                       | None                                                                                                                                    | Review agents, `retrospective` skill                                           |
| Transcript protocol      | `docs/transcripts/<date>_<slug>.md` and `-vs-state.md`                                        | None                                                                                       | None                                                                                                                                    | `process-transcript` skill, in the main session                                |
| Scratchpad               | `session-scratchpad.md`                                                                       | None                                                                                       | None                                                                                                                                    | `scratchpad` skill                                                             |
| Spec work files          | `docs/spec/work/*-gaps.md`, `spec-feedback-ST-*.md`                                           | None                                                                                       | Row status inside                                                                                                                       | Requirements and reconciliation agents                                         |

Counts. The proposals folder holds 83 files, about 310,000 words. There are 36 ADRs, 287 finding files, 58 register files, 50 handoffs, 136 reviews, 31 todo entries, and 3 transcript files.

Proposal status counts from frontmatter: 35 `implemented`, 23 `draft`, 11 `open`, 9 `superseded`, 4 `accepted`, 1 with no status (`docs/proposals/spec-code-traceability.md`). The folder does not encode the status. Eighteen `implemented` proposals and four `superseded` ones sit in the root of `docs/proposals/`, not in their subfolders.

## 2. Decision outcomes and where each is recorded

| Outcome             | Recorded as                                                                                    | Where                                                                                                                           | Quality of the record                                                                                                                                                                                                 |
| ------------------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Accepted            | `status: accepted`                                                                             | Proposal frontmatter; ADR frontmatter                                                                                           | Clean. The template says only the stakeholder accepts (`proposal.md`, comment on the Feature Request header).                                                                                                         |
| Implemented         | `status: implemented`                                                                          | Proposal frontmatter                                                                                                            | Clean.                                                                                                                                                                                                                |
| Superseded          | `status: superseded`, plus `supersedes:` on the replacement                                    | Proposal frontmatter; ADR `status: superseded by ADR-NNNN`                                                                      | Clean for ADRs. For proposals the link runs one way: the replacement points back; the old file says "Its scope is replaced by" in a quote block (`docs/proposals/superseded/containerized-agent-factory.md` line 44). |
| Deferred            | A bullet list under `**Explicitly deferred (do NOT plan stories for these):**` in 59 proposals | Proposal Scope section                                                                                                          | Prose only. No ID, no status, no owner, no trigger to revisit. A later proposal may cover the item, as `docs/proposals/run-lifecycle.md` § Scope does with `review-loop-cap.md`, but nothing tracks that.             |
| Deferred            | `status: deferred` on 5 finding files, with a todo ID in the disposition text                  | `docs/findings/IMPL-0003.md` line 43 names "deferred to todo T-0013"                                                            | Prose link only.                                                                                                                                                                                                      |
| Deferred            | Todo entry with `status: open`                                                                 | `docs/spec/work/todo.md` (25 open, 6 resolved)                                                                                  | Structured but separate from the proposal that deferred.                                                                                                                                                              |
| Cancelled           | `status: cancelled` exists in the template                                                     | No proposal uses it                                                                                                             | Defined and unused.                                                                                                                                                                                                   |
| Rejected / won't do | No status                                                                                      | Five proposals have a heading such as "Alternatives Considered" or "Non-goals"; 20 mention "rejected" or "considered" somewhere | Prose, per proposal. ADRs record rejected options inside a confirmed Pugh matrix (`docs/adr/0017-cycle-based-orchestration-supersedes-linear-playbook-fsm.md`, "The confirmed Pugh Matrix").                          |
| Waived              | `waived` on a proposal review finding                                                          | Proposal Review findings table                                                                                                  | Defined, stakeholder-only.                                                                                                                                                                                            |
| Assumption          | Kind `assumption` in the Decisions table                                                       | Proposal Appendix                                                                                                               | Becomes `decision` when confirmed. Good model for a draft-versus-settled idea.                                                                                                                                        |

The vocabulary the research question lists (do, won't do, defer, accept) maps like this: "accept" and "do" exist for proposals; "defer" exists in prose; "won't do" does not exist.

## 3. How artifacts link to each other and to their source

Links that work.

- Proposal to proposal and proposal to ADR: full markdown links, required by `rulebooks/conventions/cross-reference-format.md`. About 25 proposals link to another proposal.
- Finding to artifact: a frontmatter `artifact:` path with an anchor, and `traces:` listing IDs, for example `traces: [ADR-0026, DEC-06, DEC-17]` in `docs/findings/ATAM-0004.md`. Forty findings cite a proposal path.
- Proposal body to Decisions table: the body cites "(DEC-07)" style IDs (template comment; `docs/proposals/implemented/core-artifact-ownership.md` lines 103-169). This is the closest the repo comes to claim-to-decision links.
- Todo to source: a `- source:` line, mostly a link to a review report or a story ID (`docs/spec/work/todo.md`).
- Proposal to proposal that replaced it: `supersedes:` frontmatter, set in 8 proposals.

The cross-reference rule exempts frontmatter: "a link there would be meaningless" (`cross-reference-format.md`, Scope). So `traces:` and `supersedes:` hold plain IDs and paths. No tool in this task's scope resolves them.

Where the link to the source breaks.

- The "Raised by" cell of a Decisions table is free text. Across 303 rows the common values are "draft conversation" (8), "Jira interaction session" (6), "T-0016 grilling" (5), "Stakeholder note" (4), "counter-ids session" (4). None is a link or an ID of a stored object.
- "Decided by" is a name: "stakeholder" (200 rows), "Matthias Daues" (74), "product owner" (21), "author" (8). It is not tied to a message or a date of utterance. The Date column is the date the row was written.
- The `process-transcript` skill writes a verbatim protocol and a comparison against repository state (`packages/factory/skills/process-transcript/SKILL.md`, Outputs). The repo holds three files in `docs/transcripts/`, one of them a raw `.txt` of a podcast. Fifteen proposals mention a transcript, but the one grep for `docs/transcripts/` links in proposals and ADRs returned no hit. The skill's output is not wired to any decision row.
- Chat sessions with the agents are not stored in the repo. A decision made in one reaches the repo only if an agent writes it down.
- A handoff cites "the stakeholder in the session of 2026-11-08" (`docs/handoffs/handoff-parliament-of-choice-2026-11-09.md`, Decisions and open items). The session itself is not an addressable object.
- Finding disposition text carries the decision ("Disposition (stakeholder, 2026-11-03)") inside the finding body, not in a field.

Granularity. The unit of a record is a document. A proposal runs to 1,550 lines at most (`docs/proposals/activity-graph-orchestration.md`). The Decisions table is the only place where one idea is one row with its own ID, and the ID is local to the file: `DEC-01` exists in 19 proposals.

## 4. Where an idea gets lost today

Five concrete cases.

1. **Parliament of choice.** The handoff states it in its own words: "All decisions below come from the stakeholder in the session of 2026-11-08 and 2026-11-09, and no other durable record holds them" (`docs/handoffs/handoff-parliament-of-choice-2026-11-09.md`, Decisions and open items). Eight decisions and twelve open items live there. It also says "The factory rules require a proposal before the procedure enters the factory, and none exists." The handoff is untracked in git.
2. **Run lifecycle.** `docs/proposals/run-lifecycle.md` has no `# Appendix`, no Decisions table, and no Review findings table. Its Open Questions section reads "None." The twenty numbered decisions and the pass-1 review (7 major, 9 minor, 3 note) are in `docs/handoffs/handoff-run-lifecycle-decisions-2026-11-16.md`, an untracked file. The proposal file has uncommitted changes. A later session that reads only the proposal sees no open question and no reviewer finding.
3. **Ten of 50 handoffs are untracked.** `git ls-files docs/handoffs` returns 40. The untracked ones include the finding-classification and core-artifact-ownership handoffs. Whatever they hold exists on one machine only. Nothing in the repo points a proposal session to them either: only 4 proposals mention a handoff.
4. **The scratchpad is gitignored.** `.gitignore` line 35 excludes `/session-scratchpad.md`, and `.current-work/` on line 34. The scratchpad holds 186 lines. Examples: the 2026-09-25 list "Recover usage data, UAT installation, OnePager, OpenCode integration" has no trace of "OnePager" anywhere in `docs/` or `packages/`. The 2026-11-06 note "Findings board idea: show docs/findings/register/\*.jsonl lines as ticket cards... worth building later" appears only in four handoffs, with a throwaway spike at `poc/findings-board/` that is untracked. The 2026-07-09 entry says "Put the other two to the todo list" and the scratchpad is where the instruction stays.
5. **Stale drafts hold unfinished ideas without a decision.** Twenty-three proposals are `draft`. The oldest, `docs/proposals/proposal-traceability-map-and-naming-unification.md`, dates from 2026-08-03. `docs/proposals/concept-stage-knowledge-inventory.md` has been `draft` since 2026-09-14. Three more drafts dated 2026-11-11 (`jira-backlog-projection.md`, `machine-readable-boundary-contracts.md`, `spoken-terminal-output.md`) are untracked. Nothing records "do, won't do, defer" for a draft that stalls. It just ages.

Two weaker structural gaps.

- The todo convention names Question-category findings as todo sources (`todo-format.md`, When to file). Idea-stage questions in chat have no such rule.
- The handoff format is "a restart contract, not a transcript summary" (`handoff-format.md`). So it carries the decisions needed to restart, not every idea discussed. The handoff of 2026-11-09 shows an agent copying decisions into it because no other place exists. That is a workaround, not a designed path.

Note on tooling. In the parliament handoff, open item (k) reports that `packages/factory/scripts/handoff-lint` contradicts `handoff-format.md`. I did not verify this. It is unchecked.

## 5. What an idea-generation session would need to read, and how long that is

There is no index, no README, and no search entry point under `docs/proposals/`. A session starts with `ls` and grep.

Word counts of the candidate sources (measured with `wc -w`):

| Source                                                       | Files        | Words         |
| ------------------------------------------------------------ | ------------ | ------------- |
| Proposals, all                                               | 83           | about 309,800 |
| of which Summary sections                                    |              | about 5,900   |
| of which Decisions tables                                    | 19 proposals | about 12,400  |
| of which Open Questions sections                             |              | about 4,700   |
| of which whole Appendix (decisions, review findings, passes) |              | about 33,400  |
| ADRs                                                         | 36           | about 27,300  |
| Findings                                                     | 287          | about 82,700  |
| Handoffs                                                     | 50           | about 35,000  |
| Reviews                                                      | 136          | about 159,600 |
| Todo file                                                    | 1            | about 3,650   |
| Transcripts                                                  | 3            | about 13,700  |
| Scratchpad                                                   | 1            | about 3,100   |

Reading everything is about 636,000 words. At roughly 1.3 tokens per word that is on the order of 800,000 tokens, which exceeds one session's context. Treat the token figure as my estimate, not a measurement.

Reading only the high-value slices for an unscoped session costs less. The Summaries, Decisions tables, Open Questions, and the deferred lists total about 23,000 words. Add ADRs and the todo file and the figure is about 54,000 words, around 70,000 tokens by the same estimate. That read still misses four kinds of material:

- Proposals without a Decisions appendix. Only 19 of 83 have one, so 64 hold their decisions in running prose.
- Untracked or gitignored files: 10 handoffs, the scratchpad, and `.current-work/`.
- Everything said in chat that no agent wrote down.
- Outcomes of drafts that stalled.

A topic-scoped session does better with grep over `docs/proposals`, `docs/adr`, `docs/handoffs`, then reads the hits. Nothing makes that grep reliable, because status and topic live in prose and there are no tags. A decision on "ledger cleanup", for example, sits in the run-lifecycle handoff, an ADR on dispatch, the premerge-check marker memo, and the proposal. Four places, no shared key.

## What this means for the research question

- The Decisions table is the nearest existing unit to "one idea, one record". It has an ID, a kind, a decider, and a date. It lacks a source link, a topic link, and a global ID.
- The deferral lists, the todo file, and the finding statuses are three separate records of "later". None points at the others by a resolvable ID.
- The proposal process starts at `draft`. Nothing records an idea before a proposal file exists, and nothing records an idea that no proposal will take up.
- Frontmatter holds machine-readable fields in each file (`status`, `supersedes`, `traces`, `artifact`), and the register holds JSON per minor finding. So the repo already has parseable per-item records in two places, which a graph build could read without new authoring rules.

## Open questions

- Whether the 23 draft proposals are still live or abandoned. The files do not say, and I did not ask.
- Whether `status: cancelled` and `status: deferred` on proposals have ever been intended for use. The template defines the first and no file uses it.
- What the "Status" column of `docs/spec/work/term-candidates.md` may hold. The file has a header and no rows, and no rulebook I read defines the values.
- Whether the Decisions tables of the 64 proposals without an Appendix were ever kept elsewhere. I counted the heading, not the content, so some may hold a differently named table.
- How many decisions exist only in the 10 untracked handoffs. I read three in part. I did not count them.
- Whether `docs/spec/work/todos.md` (the older `T-01` scheme, "Factory Flow Control") and `todo.md` (the `T-NNNN` scheme) overlap in content. Both exist.
- Whether the `docs/transcripts/` output of `process-transcript` has any consumer. I found no link into it from a proposal or ADR.
- The claim in the parliament handoff that `handoff-lint` contradicts `handoff-format.md`. Unchecked.
- I did not read `packages/factory/engine/models/delivery.yaml` (the path does not exist from my working directory), so I cannot say whether an IDEA cycle in the delivery model already names a stage or artifact for raw ideas. ADR-0017 says the model declares five cycles, "IDEA, CONCEPT, ROADMAP, REFINE, REALIZE", and I did not check how the repo implements them.
