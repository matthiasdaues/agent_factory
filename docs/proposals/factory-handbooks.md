---
scope: global
schema_version: 2
title: Factory Handbooks
status: accepted
owner: md@matthiasdaues.de
created: 2026-11-25
updated: 2026-11-25
supersedes:

impact:
  scope: cross_component
  architecture_change: false  # manual override (product owner, 2026-11-26): module-graph-check reports eleven contracts that predate the feature, the same result as at baseline 4ebf5101; the handbooks add no module boundary (BUG-0150)
  external_contract_change: true
  boundaries:
    - packages/factory/docs/factory-guide.md
    - packages/factory/docs/handbook/
    - docs/handbook/
    - packages/factory/README.md
    - README.md
    - packages/factory/config/session-menu.md
    - packages/factory/agents/virgil.md
    - packages/factory/skills/newcomer-tour/SKILL.md
    - packages/factory/skills/guided-tour/SKILL.md
    - packages/factory/skills/explain-concept/SKILL.md
    - packages/factory/rulebooks/conventions/git-workflow.md
    - packages/factory/scripts/trigger
    - packages/factory/INDEX.yaml
    - docs/agent-context.md
    - docs/README.md
    - docs/arc42/concepts.md
    - docs/arc42/beginner-intro.md
    - docs/spec/scope-map.md
    - docs/spec/features/newcomer-onboarding.feature
    - docs/spec/features/opencode-cli-integration.feature
    - tests/factory/test_core_layout_references.py
    - tests/factory/test_brownfield_order.py
    - tests/factory/test_hook_missing_factory.py
    - .pre-commit-config.yaml

governance:
  assurance: routine
  risk_domains:
    - compatibility

estimate:
  as_of: 2026-11-26
  basis: decomposition
  confidence: low
  human_review_hours:
    min: 3.0
    max: 6.0
  normalized_tokens:
    min: 45000
    max: 70000
  estimated_consumption:
    min: 700000
    max: 1750000
    overhead_multiplier: 20
    playbook: feature-addition
---

# Feature Request: Factory Handbooks

## Primer

The factory is a set of agents, skills, and playbooks that a person installs into a software project. A person who runs it in their project is a user. A person who changes the factory itself, in the repository that holds its source, is a contributor. Both need to look things up in writing.

Today they find little. The user gets one guide file of 862 lines. It mixes a tutorial, explanations, recipes, and reference tables, so a user who wants one task must search the whole file. An agent that answers one question loads the whole file into its context. The contributor gets twelve lines in the root README.

The proposal replaces the guide with two handbooks, one per audience. A handbook is a folder of short Markdown pages. The user handbook ships with the factory and installs into every project. The update script replaces it with each update, so it always matches the installed code. The contributor handbook stays in this repository.

Two things sort the pages. A chapter groups pages by the concept they explain, such as installation or testing. Each page also has one type: tutorial, concept, how-to, reference, or learn. The type says what the page contains and what it leaves out. A how-to page on removing an integration holds steps with real commands and no long background.

The handbooks stay plain Markdown, because agents and terminals are their main readers. So the folder tree is the navigation. Each folder has an index file, and a script writes the page list into it between two markers. The list leaves out stubs. A stub is a page for behaviour that does not exist yet. Because the list sits in the file, an editor and an agent see the same list.

A second script checks both handbooks for missing page fields, missing index files, and out-of-date lists. This repository's pre-commit configuration runs it.

Binding rules keep one home: the main rules file and the rulebooks. A handbook page links to a rule and may repeat it only in a marked summary callout. That keeps two copies of a rule from drifting apart. Reasons for design choices stay in architecture decision records.

The first release builds the shared mechanics and moves the guide into the user handbook. It writes two contributor chapters in full and starts the others as stubs. VIRGIL, the agent that guides each session, and the tour skills point to the new pages.

## Summary

The factory gets a user handbook, which installs into every project, and a
contributor handbook, which stays in this repository. They answer one question
the factory cannot answer today: where does a person look up one task without
reading an 862-line guide from the top? Both handbooks share one page format,
one index generator, and one lint check. The first release builds these
mechanics, moves `factory-guide.md` into the user handbook, and writes the first
contributor chapters.

## Motivation

A new user today gets `packages/factory/docs/factory-guide.md`. The guide is
one file of 862 lines. It mixes a tutorial, concepts, recipes, and reference
tables. A user who wants to remove a CLI integration has to search the whole
file. An agent that answers a question about one playbook loads the
whole guide into its context.

A contributor today gets twelve lines in the root `README.md` under
"Contributing". How to write a skill sits in a rulebook. How the install model
works sits in arc42 and in ADRs. The rule "edit `packages/factory/`, never
`.agent-factory/factory/`" appears only in one paragraph of that README section
and in agent memory files.

The gigacron repository solves the same problem with a developer handbook at
`docs/handbook/`. It has about 70 pages in 14 chapters. Each page has one type,
and the folders build the navigation. This proposal takes that structure and
changes three points. The pages stay plain Markdown (DEC-01). Rules stay in the
rulebooks (DEC-02). Each audience gets its own handbook (DEC-04).

## Core Principles

- The folder tree is the navigation. A page joins the handbook when its file
  is created. Nobody maintains a page list by hand.
- Every page has exactly one type, and the type says what the page contains
  and what it does not contain.
- Each handbook has one audience. Inside a handbook, a chapter collects pages
  by the concept they explain, not by their reader.
- A handbook page describes what the code does today. A page for behaviour
  that does not exist yet stays a stub.
- Each binding rule has one home: `rules.md` and the rulebooks. A handbook page
  links to the rule and repeats it only in a `Rule summary:` callout (DEC-02).
- Rationale lives in ADRs. A handbook page links to the ADR.
- Every page reads correctly as plain Markdown, in a terminal and in an agent's
  context. No page depends on a renderer (DEC-01).
- A page earns its place when a person joining tomorrow would be confused
  without it.

## Design

### Two handbooks

| Handbook    | Path                              | Reader                                              | Ships |
| ----------- | --------------------------------- | --------------------------------------------------- | ----- |
| User        | `packages/factory/docs/handbook/` | A person who runs the factory in their project      | Yes   |
| Contributor | `docs/handbook/`                  | A person who changes the factory in this repository | No    |

The user handbook installs to `.agent-factory/factory/docs/handbook/` together
with the rest of `packages/factory/docs/`. `update-factory` replaces it with the
installed version, so the handbook always matches the installed code
(DEC-04).

### User handbook chapters

| Chapter                     | A page belongs here when it explains                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `getting-started/`          | How to install the factory and run a first session and a first playbook.                                      |
| `concepts/`                 | What agents, skills, playbooks, proposals, workstreams, and gates are, and why author and reviewer run apart. |
| `playbooks/`                | When to choose one playbook and what the user sees at each of its steps.                                      |
| `agent-context/`            | What `docs/agent-context.md` does and how to set it up and keep it current.                                   |
| `quality-and-review/`       | Gates, findings and their classification, and how to read a review.                                           |
| `branches-and-dispatch/`    | Worktrees, a run by hand and an orchestrated run, `next-id`, and merging.                                     |
| `research/`                 | Survey research and falsification research.                                                                   |
| `cli-integrations/`         | How Claude Code, Codex, Copilot CLI, Pi, and OpenCode differ, and how to add or remove one.                   |
| `installation-and-updates/` | `init-factory`, `update-factory`, removal, and the user's own changes under `user-changes/`.                  |
| `usage-capture/`            | What the usage runtime records and how to read it.                                                            |
| `reference/`                | CLI flags, the directory layout, and frontmatter fields.                                                      |
| `troubleshooting/`          | A known failure and its fix.                                                                                  |

### Contributor handbook chapters

| Chapter              | A page belongs here when it explains                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `getting-started/`   | How to clone, run `./init-factory .`, edit `packages/`, refresh the installed copy, run the tests, and make a change. |
| `architecture/`      | The packages `factory`, `orchestrator`, and `usage`, the install model, and the engine, with links to arc42 and ADRs. |
| `agents-and-skills/` | How to write an agent, a skill, or a playbook, and how `INDEX.yaml` and the generated CLI files come about.           |
| `gates-and-hooks/`   | How to add a lint script or a hook that works in every supported CLI.                                                 |
| `cli-integrations/`  | How to wire a new CLI into the factory.                                                                               |
| `testing/`           | `docs/testing.yaml`, the test layers, and a recipe per layer.                                                         |
| `workflow/`          | Proposals on `dev`, feature branches, story worktrees, commits, and how the factory is built with itself.             |
| `release/`           | Versioning, the changelog, and tags.                                                                                  |
| `contributing/`      | The page format of both handbooks, the stub rule, and the lint check.                                                 |

A page that fits two chapters goes into the chapter that owns its concept. The
other chapter links to it.

### Page format

Every page starts with frontmatter:

| Field         | Values                                                | Required | Effect                                                                                         |
| ------------- | ----------------------------------------------------- | -------- | ---------------------------------------------------------------------------------------------- |
| `title`       | Text                                                  | Yes      | Page title and link text in the generated lists                                                |
| `type`        | `tutorial`, `concept`, `how-to`, `reference`, `learn` | Yes      | Group heading in the chapter's page list                                                       |
| `status`      | `implemented`, `stub`                                 | Yes      | A `stub` page stays out of the generated lists (DEC-05)                                        |
| `description` | One sentence                                          | No       | Shown after the link in the generated lists                                                    |
| `order`       | A number, default 100                                 | No       | Sorts pages in a group, and chapters in the handbook's top-level `index.md`; lower comes first |

The `type` field sets what a page contains:

| `type`      | The reader wants to           | Contains                                                      | Does not contain                   |
| ----------- | ----------------------------- | ------------------------------------------------------------- | ---------------------------------- |
| `tutorial`  | be guided through a first run | A fixed path with checkpoints and few choices                 | Background and alternatives        |
| `concept`   | understand how it works       | A mental model, the terms, and why it is built this way       | Rules and step-by-step recipes     |
| `how-to`    | get one task done             | The task as the title, steps with real commands and paths     | Unrelated rules and long rationale |
| `reference` | look something up             | Lists, tables, flags, and signatures                          | Teaching prose and rationale       |
| `learn`     | learn a technology            | A longer text with running examples, such as Gherkin or arc42 | New rules                          |

A stub carries `status: stub`, one sentence of scope, and links to its sources.
To fill a stub, the author edits the file in place and sets
`status: implemented`.

### Binding rules

A rule that lives in two places drifts apart, so each binding rule has one home
(DEC-02). A handbook page never states a binding rule of its own. When a how-to needs a
rule to read well, it repeats the rule in a callout that links to the rule's
home:

```markdown
> Rule summary: **MUST** run `.agent-factory/factory/scripts/mdformat --number <path>` immediately after writing any markdown file.
> Source: [rules.md § Markdown formatting](../../../packages/factory/rulebooks/rules.md#markdown-formatting)
```

No lint check looks for rule words such as "must" on a handbook page. Ordinary
prose needs the word, and the author and the reviewer keep rules out of the
pages (DEC-12).

### Generated page lists

Each folder has an `index.md`. The `handbook-index` script writes the folder's
page list into that file, between two markers:

```markdown
<!-- handbook-index:start -->
<!-- handbook-index:end -->
```

The list groups pages by `type`, sorts them by `order` and then by `title`, and
leaves out stubs. The handbook's top-level `index.md` lists the chapters in the
order of the `order` field in each chapter's `index.md`. So a new chapter needs
no script change. The author writes everything
outside the markers. The script writes everything between them. So a person
who opens `index.md` in an editor and an agent that reads the file see the same
list (DEC-06).

Three rules fix the edges of the lists:

- An `index.md` never appears in its own list. It is the chapter page, and the
  top-level list links to it.
- A chapter appears in the top-level list as long as its `index.md` exists,
  even when every other page in it is a stub. So the stub chapters of the
  contributor handbook stay visible.
- An `index.md` without the marker pair is an error. The script does not add
  the markers by itself.

`handbook-index --check` exits non-zero when a list between the markers differs
from what the script would write.

### Lint check

`handbook-lint` checks both handbooks and exits non-zero when it finds:

- a page without `title`, `type`, or `status`, or with a value outside the
  tables above;
- a folder with pages but no `index.md`;
- an `index.md` without the marker pair;
- two pages in one chapter that are not stubs and have the same `title`;
- an `index.md` whose generated list is out of date (it runs
  `handbook-index --check`).

`link-check` already checks local links and anchors, so `handbook-lint` does
not check links. The pre-commit hook passes `link-check` only the files that
change. A file that links to a deleted page does not change, so the hook never
sees its broken link. That is why the migration runs `link-check` over every
live document, as "Links after the move" describes. Both scripts live in
`packages/factory/scripts/`. This repository's `.pre-commit-config.yaml` runs
them on changed handbook files. `init-factory` does not install them as hooks
in user projects, because user projects do not write factory handbook pages.

### Entry points to the handbook

- VIRGIL, `session-menu.md`, `newcomer-tour`, `guided-tour`, and
  `explain-concept` point to user handbook pages instead of
  `factory-guide.md`. `newcomer-tour` walks the `getting-started/` tutorial.
- `packages/factory/README.md` keeps install, update, and removal commands and
  links to the user handbook for everything else.
- The root `README.md` "Contributing" section links to the contributor
  handbook's `getting-started/` tutorial.
- This repository's `docs/agent-context.md` routes the concerns "write a skill
  or agent", "add a gate", and "release" to contributor handbook pages.

## Scope

**In the first release:**

- The page format, `handbook-index`, and `handbook-lint`, wired into this
  repository's pre-commit configuration.
- The user handbook with every chapter listed above. The content of
  `factory-guide.md` moves into it, split by page type.
  `factory-guide.md` is then deleted.
- The content of `docs/arc42/concepts.md` splits in two (DEC-09). "The phase
  chain" and "Key ideas" become a `concept` page in the user handbook's
  `concepts/` chapter. "Project directory tree" is corrected to name
  `packages/factory/` as the source and becomes a `reference` page in the
  contributor handbook's `architecture/` chapter. `concepts.md` is then
  deleted, and `docs/README.md` links to the two new pages.
- Every link to the three deleted files, in live documents and in records,
  points to the new home of its information.
- `docs/arc42/beginner-intro.md` is deleted. It holds only a redirect to
  `factory-guide.md`, and only backlog stories link to it (DEC-10).
- The tests and specifications that name the guide move to the new pages:
  `tests/factory/test_core_layout_references.py`,
  `tests/factory/test_brownfield_order.py`,
  `tests/factory/test_hook_missing_factory.py`,
  `docs/spec/features/newcomer-onboarding.feature`,
  `docs/spec/features/opencode-cli-integration.feature`, and
  `docs/spec/scope-map.md`.
- Every entry point listed under "Entry points to the handbook" points to the
  new pages.
- The contributor handbook with `getting-started/` and `contributing/` written
  in full. Every other contributor chapter has an `index.md` and at least one
  stub that names its sources (DEC-08).

**Explicitly deferred (do NOT plan stories for these):**

- A rendered site, for example with VitePress. A site renders Mermaid and
  zoomable diagrams better than an editor does. It waits for two reasons.
  Plain Markdown serves agents and terminals, the main readers. A site also
  adds a Node build to a Python package (DEC-01).
- Generating `rules.md` from markers in handbook pages. Rules stay in the
  rulebooks (DEC-02).
- Handbook mechanics for user projects, so that a project can keep its own
  handbook the way gigacron does. No user project has asked for it.
- Filling the contributor chapters beyond the stubs. Each chapter fills when a
  contributor needs it. The one exception is the directory-tree `reference`
  page in `architecture/`, which the first release writes in full.
- Changing the playbook concept, and keeping playbook pages in step with the
  playbook files. The `playbooks/` chapter documents the playbooks that exist
  today (DEC-11). A separate proposal rethinks the playbook concept. It lists
  `packages/factory/docs/handbook/playbooks/` in its boundaries and rewrites
  the chapter in the same change as the playbooks.

## Design Details

- **Deleting `factory-guide.md`.** `update-factory` replaces the whole installed
  copy, so every factory file that links to the guide changes in the same
  update. A link from a user's own document to
  `.agent-factory/factory/docs/factory-guide.md` breaks after the update. The
  `CHANGELOG.md` entry names the move and the new path
  (`.agent-factory/factory/docs/handbook/`) (DEC-07).
- **Links after the move.** A live document is every tracked Markdown file
  outside `poc/` and outside the record folders listed in the next item.
  `poc/` holds throwaway spikes. After the move, `link-check` runs over every
  live document and exits 0. So no live link points to `factory-guide.md`,
  `concepts.md`, or `beginner-intro.md`.
- **Records outside the move.** The record folders are `backlog/`,
  `docs/handoffs/`, `docs/findings/`, `docs/reviews/`, `docs/transcripts/`,
  `docs/research/`, `docs/spec/work/`, `docs/proposals/implemented/`,
  `docs/proposals/superseded/`, and `~archive/`. Their files keep their wording.
  Only the targets of links to the three deleted files change.
- **Deleted, not archived.** `factory-guide.md`, `concepts.md`, and
  `beginner-intro.md` are deleted, not moved under `~archive/`. Their content
  lives on in the handbooks, and git history keeps the old text (DEC-13).
  Every link to one of the three files moves to the new home of its
  information, in live documents and in records alike (DEC-14).
- **Repointing links.** The migration map assigns each section of the three
  files to the handbook page that now holds it. A link with an anchor points
  to the page, and the anchor if one exists, that holds its section. A link
  without an anchor points to the page that holds the file's opening: the user
  handbook's top-level `index.md` for `factory-guide.md`, the `concept` page
  for `concepts.md`, and the `getting-started/` tutorial for
  `beginner-intro.md`. The rewrite reuses `_link_rewrite.py`, the module of
  `move-docs`. At the reviewed commit, 86 links in 36 files point to the three
  files.
- **Voice.** Every handbook page follows
  [factory-voice.md](../../packages/factory/rulebooks/conventions/factory-voice.md).
  `handbook-lint` does not check prose. The lector agent reads the migrated
  user handbook once before release.

## Open Questions

No open questions remain.

## Completion Criteria

- `handbook-lint` exits 0 on both handbooks, and exits non-zero on a test page
  for each failure the lint section lists.
- `handbook-index --check` exits 0 on both handbooks.
- `link-check` over every live document, as "Links after the move" defines it,
  exits 0.
- `handbook-index` and `handbook-lint` exit non-zero on an `index.md` without
  the marker pair, and no `index.md` lists itself.
- This repository's `.pre-commit-config.yaml` runs `handbook-lint` on changed
  handbook files, and a commit with a page that lacks `type` fails.
- `packages/factory/docs/factory-guide.md` does not exist, and
  `rg factory-guide packages/ tests/ docs/spec/ README.md --glob '!CHANGELOG.md' --glob '!docs/spec/work/**'`
  finds no match, and the full test suite passes. The
  `CHANGELOG.md` entry of the release names the new path.
- Every section heading of the deleted guide maps to a user handbook page, and
  the migration story records that map.
- No tracked Markdown file outside `.agent-factory/` holds a link to
  `factory-guide.md`, `docs/arc42/concepts.md`, or
  `docs/arc42/beginner-intro.md`. `link-check` reports no problem for any
  rewritten link, in live documents and in records.
- `docs/arc42/concepts.md` and `docs/arc42/beginner-intro.md` do not exist.
  The phase chain and the key ideas are on a user handbook `concept` page.
  The corrected directory tree is on a contributor handbook `reference` page.
- After `update-factory`, `.agent-factory/factory/docs/handbook/index.md`
  exists and lists every user handbook chapter.
- Choosing H in the session menu as a new user starts the
  `getting-started/` tutorial of the user handbook.
- The contributor handbook's `getting-started/` tutorial takes a person from
  `git clone` to a passing test run, using only commands that exist in the
  repository.
- The contributor handbook's `contributing/` chapter describes the page
  format, the stub rule, and both scripts. Every other contributor chapter has
  an `index.md` and at least one stub that names its sources.
- `packages/factory/README.md` and the root `README.md` link to the handbooks
  as "Entry points to the handbook" describes, and `docs/agent-context.md`
  routes the three named concerns to contributor handbook pages.
- The lector agent's report on the migrated user handbook exists, and its
  fixes are applied.

## Guiding Rule

A person reads one page, in a terminal or in an agent's context, and can do
the task the title names.

# Appendix

## Decisions

| ID     | Date       | Kind     | Decided by    | Decision                                                                                                                                                                                                      | Raised by                       |
| ------ | ---------- | -------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------- |
| DEC-01 | 2026-11-25 | decision | product owner | The handbooks stay plain Markdown. A VitePress site is a later addition, kept for its better rendering of diagrams.                                                                                           | session, rendering question     |
| DEC-02 | 2026-11-25 | decision | product owner | Binding factory rules stay in `rules.md` and the rulebooks. Handbook pages link to them and do not hold rules of their own.                                                                                   | session, rules question         |
| DEC-03 | 2026-11-25 | decision | product owner | One proposal covers both handbooks, because they share the page format, the index generator, and the lint check.                                                                                              | session, proposal question      |
| DEC-04 | 2026-11-25 | decision | product owner | There are two handbooks, one per audience: the user handbook ships with the package, the contributor handbook stays in this repository.                                                                       | session, initial request        |
| DEC-05 | 2026-11-25 | decision | product owner | The `status` field has two values, `implemented` and `stub`. Gigacron's `specified` and `planned` exist only on its older pages.                                                                              | gigacron comparison             |
| DEC-06 | 2026-11-25 | decision | product owner | Generated page lists are written into each `index.md` between markers, so the file reads correctly without a renderer.                                                                                        | DEC-01                          |
| DEC-07 | 2026-11-25 | decision | product owner | `factory-guide.md` is deleted, not kept as a redirect, because `update-factory` replaces every factory file that links to it.                                                                                 | Breakage Test                   |
| DEC-08 | 2026-11-25 | decision | product owner | The first release writes the contributor chapters `getting-started/` and `contributing/` in full and leaves the other chapters as stubs.                                                                      | scope                           |
| DEC-09 | 2026-11-25 | decision | product owner | `docs/arc42/concepts.md` splits: the phase chain and key ideas go to the user handbook, the directory tree goes to the contributor handbook.                                                                  | grilling, question 1            |
| DEC-10 | 2026-11-25 | decision | product owner | `docs/arc42/beginner-intro.md` is deleted, because it holds only a redirect to the deleted guide and only records link to it.                                                                                 | grilling, question 1            |
| DEC-11 | 2026-11-25 | decision | product owner | The `playbooks/` chapter documents today's playbooks. The rethink of the playbook concept is a separate proposal that rewrites the chapter.                                                                   | grilling, question 6            |
| DEC-12 | 2026-11-25 | decision | product owner | `handbook-lint` does not check for rule words such as "must" in any form. Rules stay out of the pages by authoring and review.                                                                                | lector structural pass, item 16 |
| DEC-13 | 2026-11-25 | decision | product owner | The three replaced files are deleted, not archived under `~archive/`. Their content moves into the handbooks and git history keeps the old text, so the archive rule of `rules.md` § Handoffs does not apply. | review pass 1, PROP-01          |
| DEC-14 | 2026-11-25 | decision | product owner | Every link to the three deleted files, records included, is repointed to the new home of its information. Records change only in link targets.                                                                | review pass 1, PROP-01          |

## Review findings

| ID      | Pass | Severity | Check | Status   | Finding                                                                                                                                                                                                                                                                                                                                                                                                                               | Resolution                                                                                                                                                                                                                                                                                                |
| ------- | ---- | -------- | ----- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PROP-01 | 1    | major    | 01    | resolved | Lines 238–242 and 316–345 rely on `link-check`, but the hook receives changed Markdown files. Unchanged links to the deleted guide can survive the proposed checks. Add a link check for both handbooks in their intended locations and account for inbound links from live documents and historical records. Severity: major, because the proposed checks can pass while a live link is broken (`fails_purpose`).                    | Design Details "Links after the move" defines a live document and requires `link-check` over all live documents to exit 0; the Lint check section says why the hook alone misses these links; a completion criterion checks it. Baseline at the reviewed commit: `link-check` over live documents passes. |
| PROP-02 | 1    | major    | 02    | resolved | Lines 265–277 require a finished reference page in `architecture/`, while lines 289–290 defer all contributor content beyond the stubs. Name the directory reference as an explicit first-release exception and say whether `architecture/` still needs a stub. Severity: major, because a planner can defer a page required for release (`fails_purpose`).                                                                           | The deferral "Filling the contributor chapters beyond the stubs" names the directory-tree `reference` page in `architecture/` as its one exception.                                                                                                                                                       |
| PROP-03 | 1    | major    | 03    | resolved | Lines 262–264 and 323–327 delete the guide without assigning its consumers outside `packages/` to the migration. Three factory tests read it directly, and the newcomer and OpenCode feature files name it. Add those tests and live specifications to the migration, with their checks and references moved to the new pages. Severity: major, because the proposed migration leaves tests reading a deleted file (`fails_purpose`). | The three tests, the two feature files, and `docs/spec/scope-map.md` are in Scope and in `impact.boundaries`; the completion criterion searches `packages/`, `tests/`, `docs/spec/` and `README.md` and requires the full test suite to pass.                                                             |
| PROP-04 | 1    | major    | 03    | resolved | Lines 166–174 and 206–235 leave the status and placement of chapter indexes unclear. A stub-only chapter may disappear from the root list or include its own `index.md` in its page list. Define which indexes appear in each list, which fields apply to them, and what the generator does with a missing marker pair. Severity: major, because a planner has to choose the navigation and lint behavior (`fails_purpose`).          | "Generated page lists" adds three rules: an `index.md` never lists itself, a chapter with an `index.md` stays in the top-level list, and an `index.md` without the marker pair is an error. The lint list and a completion criterion cover the third rule.                                                |
| PROP-05 | 1    | minor    | 03    | open     | Line 142 names `user-changes/`, while the existing update guide and package README identify `.agent-factory/factory-user-changes/<timestamp>/`. Use the current path in the chapter brief. Severity: minor, because the migration has the correct source text but the brief sends the reader to the wrong directory (`raises_cost`).                                                                                                  |                                                                                                                                                                                                                                                                                                           |
| PROP-06 | 1    | minor    | 05    | open     | Lines 16–17 list two handbook directories that are absent at the reviewed commit. Keep the new directories in Scope and use tracked paths for the review boundaries. Severity: minor, because the handbook locations are clear but a reviewer cannot inspect the paths as existing boundaries (`raises_cost`).                                                                                                                        |                                                                                                                                                                                                                                                                                                           |
| PROP-07 | 2    | minor    | 01    | open     | The update check at lines 392–393 opens the installed index but checks links only in the source checkout. Check user handbook links after installing into a separate project, where links to files outside the package can fail. Severity: minor, because planning can proceed and a user could discover a broken link after installation (`raises_cost`).                                                                            |                                                                                                                                                                                                                                                                                                           |
| PROP-08 | 2    | minor    | 03    | open     | Lines 351–359 call for splitting links by section with `_link_rewrite.py`. The current helper maps one old path to one new path and keeps the old anchor. Specify how the migration applies the section map to each link. Severity: minor, because the destination rule is clear and the planner must inspect the helper to see which part needs extra work (`raises_cost`).                                                          |                                                                                                                                                                                                                                                                                                           |
| PROP-09 | 2    | minor    | 03    | open     | The migration list at lines 296–302 misses the context-fold scenario that names the deleted concepts page. Update its example document in [core-artifact-layout.feature](../spec/features/core-artifact-layout.feature#L391). Severity: minor, because the scenario can still use a fixture but the example gives readers a path the factory repository no longer has (`raises_cost`).                                                |                                                                                                                                                                                                                                                                                                           |

## Review passes

| Pass | Date       | Reviewed commit                          | Disposition | Failed checks  | Summary                                                                                                                                                                                                                                |
| ---- | ---------- | ---------------------------------------- | ----------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1    | 2026-11-25 | d777b6ecec30bdbdfadb47f3a95fa8f423c7e045 | findings    | 01, 02, 03, 05 | The impact classification, open questions, motivation, and estimate pass. Define the migration checks, contributor scope, and index behavior, and use tracked review boundaries.                                                       |
| 2    | 2026-11-25 | 86894b1790d0af2fcdd9425ad510aa277c691a28 | findings    | 01, 03, 05     | The four fixes from pass 1 resolve their findings. Add an installed link check, explain how the rewrite uses the section map, and update the context-fold example. The two proposed handbook directories remain absent at this commit. |
