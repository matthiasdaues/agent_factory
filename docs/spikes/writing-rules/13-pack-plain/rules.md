# Rules

Each rule takes one line. Some are short sayings; the rest use the keywords of **RFC 2119** (MUST / MUST NOT / SHOULD). Each section links to the rulebook that explains its rules in detail. The reasons, examples, and edge cases are in that rulebook, not here. This file says *what* to do; the rulebook says *why* and *how*.

## General principles

- Small is beautiful
- Small steps are better than big ones
- Quality is what satisfies a given use case
- Keep it simple
- Better done than perfect

## Working with the CLI

- **MUST** use `rg` with an explicit search of hidden files, or `bash` (`find`, `fd`, etc.), when the file you look for may be in a hidden directory or be a hidden file.
- **MUST** look up a skill in the local INDEX.yaml first. Use the global skill/agent directory only if the local INDEX.yaml does not list the skill. If the local INDEX.yaml is missing or cannot be read, stop and tell the user; do not go on with only part of the Factory guidance. The local skill directory for each CLI:
  - Claude Code: `.claude/skills/<name>/SKILL.md`, `.claude/agents/<name>.md`
  - GitHub Copilot CLI: `.github/skills/<name>/SKILL.md`, `.github/agents/<name>.md`
  - Pi: `.pi/skills/<name>/SKILL.md`, `.pi/agents/<name>.md`
  - Codex: `.agents/skills/<name>/SKILL.md`, `.codex/agents/<name>.toml`
- **MUST** read the local INDEX.yaml first (`.claude/INDEX.yaml` for Claude Code, `.github/INDEX.yaml` for GitHub Copilot CLI, `.pi/INDEX.yaml` for Pi, `.codex/INDEX.yaml` for Codex). It lists all agents, skills, and playbooks that are available locally. **Codex**: map each `path:` entry in INDEX.yaml to its file. Agents map to their generated files under `.codex/agents/` (e.g. `agents/virgil.md` → `.codex/agents/virgil.toml`). Skills map to `.agents/skills/` (e.g. `skills/grilling/SKILL.md` → `.agents/skills/grilling/SKILL.md`). If `.codex/` does not exist, see the source-repo fallback below.
- **MUST (Pi only)**: Pi cannot start subagents by itself. To run a factory *agent*, not a skill, call the `run_agent` tool (the `run-agent` extension adds it) with the agent name and the task. Do not read `.pi/agents/<name>.md` and play the agent in the current session. `run_agent` starts the agent in a separate Pi session, and that separate session keeps the author and the reviewer independent. To run several agents in parallel that touch different files, call `dispatch_wave` (the `dispatch-wave` extension adds it). It gives each agent its own git worktree and merges through `premerge-check`. Claude Code, Codex and GitHub Copilot CLI start subagents themselves and need neither tool.
- **MUST (Codex only)**: Map Factory agents to their generated files under `.codex/agents/`. When the user picks an agent for interactive work, take on that role in the current session, unless the agent file requires a separate session. Start a native custom agent when a playbook hands out work, when the author and the reviewer must work in separate sessions, or when work runs in parallel. **MUST NOT** write an artifact and do its independent review in the same session. Use `.codex/playbooks`, `.codex/rulebooks`, and `.codex/scripts` for the Factory aliases. **Source-repo fallback:** if `.codex/` does not exist but `packages/factory/` does, you are in the Agent Factory source repository. Map `path:` entries directly under `packages/factory/` (e.g. `agents/virgil.md` → `packages/factory/agents/virgil.md`) and read the Markdown source as you would under Claude Code or Copilot CLI.
- **MUST** use full 40-character Git SHAs in gates, markers, dispatch records, and handoffs that scripts read. Short SHAs are only for display.

## Basic principles

→ [foundational-principles.md](conventions/foundational-principles.md), [factory-voice.md](conventions/factory-voice.md)

- **MUST** write every text, chat included, in the style that [factory-voice.md](conventions/factory-voice.md) defines, and run its checks before sending while you write each sentence, not afterwards.
- **MUST** ask the user every decision with one concrete case and the result of each option for that case, as [Decision questions](conventions/factory-voice.md#decision-questions) describes, in every CLI and every skill.
- **MUST** keep each message between skills or agents short, and make each one checkable on its own.
- **MUST** keep creation and checking apart: agents create artifacts, and gates that fire automatically run scripts that check them against fixed criteria that depend on the current state.
- **MUST** build only what the specification requires, in the smallest step that can be checked (YAGNI).

## Working discipline

→ [working-discipline.md](conventions/working-discipline.md)

- **MUST** check a premise before you build an explanation on it; stop and check when a result is unexpected or the explanation gets long.
- **MUST** handle an error in three steps: say it plainly, find its cause, and change the process.
- **MUST** stop fixing an approach after the same kind of error happens twice; report it and propose another approach or an earlier decision to look at again.
- **MUST NOT** state how a tool or an external product behaves unless you checked it in this session; otherwise mark the claim as unchecked and name what would check it.
- **MUST** check an invented example for names, dates, and facts that contradict each other or the project.
- **MUST** prefer removing a claim from a document over building what the claim describes, unless you can name a concrete system that breaks without it.

## Proposals

→ [proposal.md template](templates/proposal.md), [feature-addition.md](../playbooks/feature-addition.md)

- **MUST** start a feature-addition from a proposal that follows the [proposal template](templates/proposal.md) at `docs/proposals/<name>.md`. The Planning phase reads it as the source of the design.
- **MUST** clarify or grill a feature proposal in the file itself; an
  interview that settles every decision may move it from `draft` to `open`,
  but only the stakeholder's approval may move it to `accepted`.
- **MUST** start specification, architecture, or planning work from an
  `accepted` proposal and choose those phases from the impact it declares.
- **MUST NOT** list a `docs/proposals/*` file in the `inputs:` of a shipped agent. A proposal is where the design comes from, not a file the agent reads at run time. Point `inputs:` at tracked, shipped files (the playbook, policies, and schemas the agent reads).

## Architecture documentation

→ [brownfield-onboarding.md § Step 2.3 — Build architecture.dsl](../playbooks/brownfield-onboarding.md#step-23--build-architecturedsl), [architecture-agent.md § Workflow](../agents/architecture-agent.md#workflow)

- **MUST** run Stage 1 of brownfield onboarding in this order: archive the outdated documentation, build the scope map with `reverse-map`, then create `docs/spec/architecture.dsl` and fill it from the code before you write architecture text.
- **MUST** model deployment nodes and connections in the Deployment view of `architecture.dsl` from Terraform (or other infrastructure code) when it exists.
- **MUST** treat arc42 chapters 05, 06, and 07 as explanations derived from the `architecture.dsl` views, not as separate sources.
- **MUST** set `"arc42.projected" "false"` in the workspace `properties` block when you create a new `architecture.dsl`; only the architecture-agent sets it to `"true"`, and only when the user asks for the arc42 chapters to be generated.

## Agent context

→ [agent-context-composition.md](conventions/agent-context-composition.md)

- **MUST** fill `docs/agent-context/` as the place where the factory reads project knowledge.
- **MUST** set `mode: primary` when the index files are the main source of decisions.
- **MUST** set `mode: index` when the index files are copies drawn from existing documentation.
- **MUST** add a `source:` pointer to every leaf field that is not null and not deferred when `mode: index`.
- **MUST NOT** edit an index file with `mode: index` by hand (edit `docs/agent-context.md` directly).
- **MUST NOT** write back to the sources: edits to `docs/agent-context/*.yaml` never reach the source documents.
- **MUST NOT** put `source:` pointers in `reading-guides.yaml`.
- **MUST NOT** use both the YAML agent-context format and the markdown charter format in one project.
- **MUST** point `source:` at the project's own convention when it exists, not at the factory rulebook default that it replaces.

## Testing

→ [testing-strategy.md](conventions/testing-strategy.md)

- **MUST** give each contract you can observe one test layer that owns it, and make that owner stronger before you add overlapping tests.
- **MUST** pick test cases by equivalence class, boundary, or separate way of failing, never to reach a count that only looks good or a fixed coverage percentage.
- **MUST NOT** repeat a rule of a deterministic linter in pytest.
- **MUST NOT** repeat or replace a team's existing lint and format tools. Factory linters check only the shapes of factory artifacts that the team's tools do not know.
- **MUST** accept a test that would catch a change in meaning that no existing linter or structure check can see, even when the contract already has a structural owner.
- **MUST** show that the remaining owner detects a typical fault before you delete overlapping tests.

## Branches

→ [branching-policy.md](conventions/branching-policy.md)

- **MUST** create every new local branch together with its own linked worktree in one step, using `git worktree add -b <branch> .current-work/<feature-branch>/<branch> <base>`. **(automated only)** In manual mode, work happens directly in the primary checkout, and no worktrees are created.
- **MUST** put every worktree under `.current-work/<feature-branch>/`, never in the repository root, a sibling directory, or any other path.
- **MUST** check every new branch-to-worktree mapping with `git worktree list --porcelain` before you work on that branch.
- **MUST** create exactly one feature branch per story or bug, never per EPIC, sprint, or wave.
- **MAY** create and commit a numbered artifact (backlog story, finding, proposal, or any other file with a sequential ID) on any branch. For each prefix it serves, `next-id` hands out IDs from one counter shared by all branches, so IDs do not collide. The prefixes are listed in [id-prefixes.md](conventions/id-prefixes.md). `PROP` rows in a proposal, the split letters of a story, and other IDs follow their own numbering rule and do not use the counter.
- **MUST** create every new invocation branch from `dev` (not `main`), named `feature/<proposal-title>`. An existing review branch that you take over keeps its name and history and records the current `HEAD` as its review root. Story branches are created from the invocation branch.
- **MUST** create every feature branch and worktree from the invocation branch, and record the commit it started from as the branch root.
- **MUST** decide the merge order from a real check of which files overlap, not from a group label. Branches that touch different files merge in parallel; branches that overlap merge one after another in dependency order.
- **MUST** run the full test suite after every merge, before the next one.
- **MUST** track exactly two commit IDs per invocation: the branch root and the branch head.
- **MUST** run `.agent-factory/factory/scripts/verify-base` from the main checkout (a linked worktree has no copy of its own) as the first tool call of a subagent in its own worktree, against its target branch and the base SHA it declared; stop on any non-zero exit before you read, edit, or commit anything.
- **MUST** run `.agent-factory/factory/scripts/premerge-check` on a finished branch before you merge it; a non-zero exit blocks the merge until someone looks into it.

## Dispatch

→ [dispatch-contract.md](conventions/dispatch-contract.md)

The rules in this section apply to both modes unless they are marked **(automated only)**. In **manual** mode, the human owns all commits, pushes, and gate decisions; dispatch scripts, ledgers, and automatic checks are not used.

- **MUST** give each sub-agent an instance ID it can find and report back to, never the agent-type name of the parent.
- **MUST** start a sub-agent fresh, with a [brief file](conventions/dispatch-contract.md#brief-file), unless it needs the conversation itself; after the context was compacted, always start it fresh. This applies in every CLI ([Fresh Agent Or Inherited Context](conventions/dispatch-contract.md#fresh-agent-or-inherited-context)).
- **MUST NOT** wait forever for a sub-agent's reply. Do the work yourself if it refuses or does not answer.
- **MUST** split a dispatch that covers the whole codebase into smaller dispatches that can each be merged on their own, instead of running it as one.
- **MUST** commit between the rounds of a long-running dispatch, so its progress is saved.
- **MUST** check a sub-agent's reported result against what you can see (git, tests, gates) before you treat the work as done. The automatic gates decide, not the sub-agent's own report. **(automated only)**
- **MUST** check that every reported commit SHA exists (`git cat-file -e <sha>^{commit}`) and is on the expected branch (`git branch --contains <sha>`) before you accept a sub-agent's claim that it is done. **(automated only)**
- **MUST NOT** start a new agent for the same role while an earlier one is still running. The earlier one cannot be cancelled and will use tokens on outdated state.
- **MUST** check that every story in a wave has reached a final state (merged, or marked blocked or failed in the dispatch ledger) before you start the next wave. **(automated only)**
- **MUST** commit or record each story's result (merged SHA or the reason it is blocked) before the wave counts as closed. **(automated only)**
- **MUST** close every dispatch as completed or abandoned. A dispatch that starts and never closes is lost. **(automated only)**
- **MUST** keep a dispatch ledger (`.current-work/<feature-branch>/dispatch-ledger.yaml`) that records each story's branch, worktree, declared base, gate results, commit SHA, merge SHA, and status. **(automated only)**
- **MUST** update the `status` field of the story file in the same commit that delivers the story's code. **(automated only)** In manual mode, the human makes this commit.
- **MAY** run `next-id` in manual mode and let it push the claim ref. This push by `next-id` is the only exception to the rule that the human does all pushes. The human does every other push.

## Step limits

No hook enforces these rules yet. The `step-guard` hook is installed, but it does not find or apply the manifests. Agents keep within the step limits on their own.

- **MUST** write a step manifest from the `inputs`, `outputs`, and `max_input_tokens` that the playbook declares, for steps that are not dispatch steps.
- **MUST** write a step manifest from the `outputs` and `tests` in the story frontmatter, for dispatch steps.
- **MUST** treat the active step manifest as the limit of what the running step agent may read and write.
- **MUST NOT** read outside the manifest's declared inputs or write outside its declared outputs while the manifest is active.
- **MUST** keep the manifest schema in line with the step declaration block in the playbook and with the guard loader.

## Commits

→ [commit-conventions.md](conventions/commit-conventions.md)

- **MUST** put the story or bug ID in parentheses in every implementation commit: `<type>: <description> (<ID>)`.

## Git workflow

→ [git-workflow.md](conventions/git-workflow.md)

- **MUST** run git as a command on its own, never after `cd` or another command on the same line (the working directory stays set; the guardrail misreads combined lines).
- **MUST NOT** switch the current checkout to create a branch in automated mode; automated branches use their own linked worktree with `git worktree add -b`. In manual mode, the human may create or take over a branch directly in the primary checkout.
- **MUST** run `.agent-factory/factory/scripts/premerge-check <target> <branch>` before `git merge <branch>`. The merge is blocked without the `.current-work/premerge-check-ok` marker that the check writes. **(automated only)**
- **MUST NOT** skip a failing pre-commit hook (`--no-verify`, `core.hooksPath`); fix the problem the hook reports. Discard changes with `git checkout HEAD -- <path>`, not `git checkout .`.
- **SHOULD** commit through the hooks in two passes: `add` → `commit`; if the hook says "files were modified by this hook", `add -u` → commit again. Or use `.agent-factory/factory/scripts/commit-safe`.
- **MUST** remove a clean worktree and safely delete its merged branch after its target passes the checks, unless the branch is still named as an active review base.
- **MUST** use full 40-character SHAs in gates, markers, dispatch records, and handoffs that scripts read; short SHAs are only for display.
- **MUST** claim every ID of a prefix that `next-id` serves through `next-id`, in manual and in automated mode. This push by `next-id` is the only exception to the rule that the human does all pushes; in manual mode, the human does every other push. A push outside `next-id`, such as `git -C . push` with a claim commit written by hand, can move the counter back to an older value, and then IDs repeat.

## Handoffs

→ [handoff-format.md](conventions/handoff-format.md)

- **MUST** put one section with the current state, which counts as the truth, before any optional history.
- **MUST** record the exact local and upstream tips and the exact ahead/behind counts; branch labels and rough counts are not enough.
- **MUST** replace or move outdated instructions instead of leaving them mixed with current open work.
- **MUST** move outdated documentation files under `~archive/` and keep their original relative path (for example, `docs/arc42/old.md` → `~archive/docs/arc42/old.md`).

## Research

→ [research-directory-layout.md](conventions/research-directory-layout.md)

- **MUST** put each research effort in its own slug directory, `docs/research/<slug>/`, never directly under `docs/research/`.

## Links between files

→ [cross-reference-format.md](conventions/cross-reference-format.md)

- **MUST** write every reference to another artifact in this repo (ADR, finding, todo entry, rulebook, skill, agent, spec document) as a full markdown link, never as a bare ID, code span, or text in parentheses.
- **MUST** point every link at the exact section of the target when the target has sections.

## Findings

→ [finding-format.md](conventions/finding-format.md)

- **MUST** classify every finding by [finding-classification.md](conventions/finding-classification.md), and file every blocking finding as its own `docs/findings/<TAG>-NNNN.md`.
- **MUST** say in every finding both what is wrong and what to do.

## Markdown formatting

→ [markdown-formatting.md](conventions/markdown-formatting.md)

- **MUST** run `.agent-factory/factory/scripts/mdformat --number <path>` right after you write any markdown file, not later in `validate` or the pre-commit hook.

## Mermaid

→ [mermaid-notation.md](conventions/mermaid-notation.md)

- **MUST NOT** put plain semicolons in Mermaid blocks; write one statement per line and write a semicolon that must appear in the text as `#59;`.

## Repeat reviews

→ [review-loop-discipline.md](conventions/review-loop-discipline.md)

- **MUST** run the deterministic check again on every repeat review pass.
- **MUST** check each earlier finding one by one on a repeat review pass.
- **MUST** run the full review again from the start on a repeat review pass, not only the list of earlier findings.

## State machines

→ [state-machine-notation.md](conventions/state-machine-notation.md)

- **MUST** treat event-driven pseudocode as the only source of truth for state machines. Mermaid is generated from it and never written first.
- **MUST** keep every `ChangeState(X)` in the pseudocode and its Mermaid edge exactly matched, with no differences.

## Todos

→ [todo-format.md](conventions/todo-format.md)

- **MUST** write every deferred decision or open question as an entry in `docs/spec/work/todo.md`, not leave it unspoken in the conversation.
- **MUST** get the number of each todo entry with `.agent-factory/factory/scripts/next-id T` and read it from standard output. When `next-id` fails, stop and report its message; never choose a number by hand.

## Versions

→ [versioning-policy.md](conventions/versioning-policy.md)

- **MUST** keep the git tag and the version file the same, with no differences.
- **MUST NOT** tag feature branches, or use release or pre-release tag formats on a branch other than main.

## Start of YAML files

→ [yaml-format.md](conventions/yaml-format.md)

- **MUST** start every YAML file the factory writes, and every example of a whole YAML file, with `---`; mark an excerpt with `<!-- yaml-excerpt -->` and leave out the `---`.

## Referenced from

- [foundational-principles.md](conventions/foundational-principles.md)
- [factory-voice.md](conventions/factory-voice.md)
- [working-discipline.md](conventions/working-discipline.md)
- [agent-context-composition.md](conventions/agent-context-composition.md)
- [branching-policy.md § Project-Specific Rules](conventions/branching-policy.md#project-specific-rules)
- [dispatch-contract.md § Project-Specific Rules](conventions/dispatch-contract.md#project-specific-rules)
- [commit-conventions.md § Story/Bug ID Required](conventions/commit-conventions.md#storybug-id-required)
- [cross-reference-format.md § Rule](conventions/cross-reference-format.md#rule)
- [finding-format.md § When to file](conventions/finding-format.md#when-to-file)
- [finding-classification.md § Referenced from](conventions/finding-classification.md#referenced-from)
- [markdown-formatting.md § Rule](conventions/markdown-formatting.md#rule)
- [mermaid-notation.md § Rule](conventions/mermaid-notation.md#rule)
- [review-loop-discipline.md § Rule](conventions/review-loop-discipline.md#rule)
- [state-machine-notation.md § Canonical Format](conventions/state-machine-notation.md#canonical-format)
- [versioning-policy.md § Git Tag Must Match Version File](conventions/versioning-policy.md#git-tag-must-match-version-file)
- [yaml-format.md § Rule](conventions/yaml-format.md#rule)
