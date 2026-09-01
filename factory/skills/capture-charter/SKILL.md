---
name: capture-charter
description: >-
  Scaffold, scan, or complete the project charter under docs/charter/ — three
  modes: --init creates the skeleton from templates, --init --scan
  pre-populates it from an existing codebase, and the completeness sweep (no
  flag) forces every remaining decision and derives Epic 0 setup stories.
  Use when starting a new project's charter, onboarding a brownfield
  codebase, or running the pre-planning completeness sweep.
category: requirements
version: 1.0.0
disable-model-invocation: false
---

# Capture Charter

Lifecycle skill for `docs/charter/` — the three documents (`tech-stack.md`,
`development.md`, `house-rules.md`) that answer what a developer needs to
know before writing the first line of code. See
[capture-project-constraints.md](../../../docs/proposals/implemented/capture-project-constraints.md)
for the full design rationale.

**Runs in the orchestrating session, never as a spawned subagent.** Every
mode either asks the stakeholder questions or presents findings for
confirmation — the stakeholder must be present to answer.

This skill *creates and completes* the charter. To *amend* a single section
later — a technology choice settled mid-phase, a house rule that surfaces
during review — use `update-charter` instead; it owns incremental writes to
`docs/charter/*.md` on behalf of any agent.

## Charter structure

Three documents, one skeleton each at
`factory/rulebooks/templates/charter-tech-stack.md`,
`charter-development.md`, `charter-house-rules.md`. Every section starts as
an HTML-comment prompt followed by `To be decided.` — see the templates for
the exact section list per document. See
[update-charter § Charter structure](../update-charter/SKILL.md#charter-structure)
for what each document is for.

## Mode selection

| Invocation                      | Mode                | When                                                     |
| ------------------------------- | ------------------- | -------------------------------------------------------- |
| `capture-charter --init`        | Greenfield scaffold | Right after vision capture, before requirements          |
| `capture-charter --init --scan` | Brownfield scan     | After brownfield onboarding's architecture review passes |
| `capture-charter`               | Completeness sweep  | Before the planning gate, after architecture settles     |

## Mode 1 — `--init` (greenfield)

### Step 1 — Create the skeleton

Copy the three templates to `docs/charter/tech-stack.md`,
`docs/charter/development.md`, `docs/charter/house-rules.md`, preserving
every section heading. Strip nothing else — the HTML-comment prompts and
`To be decided.` placeholders stay until a section is actually filled.

### Step 2 — Fill known answers

Read back the vision conversation (`capture-vision`'s six facets, or
whatever the stakeholder has already said). Map anything already decided
onto the matching charter section — most commonly the **Constraints** facet
naming a language, framework, or platform. Do not invent answers to fill
gaps; leave every section without a real answer as `To be decided.`

### Step 3 — Validate and format

Run `factory/scripts/charter-lint` (default, structural mode) — confirms
all three files exist, every template section is present, no section is
byte-empty. Fix any finding before proceeding. Format each file with
`factory/scripts/mdformat --number docs/charter/<document>.md` per
[markdown-formatting.md](../../rulebooks/conventions/markdown-formatting.md).

### Step 4 — Commit

```
docs: scaffold project charter (--init)
```

**Completion**: all three charter files exist, `charter-lint` (default
mode) passes, known answers recorded, everything else reads `To be decided.`.

## Mode 2 — `--init --scan` (brownfield)

### Step 1 — Scan the codebase

Look for existing configuration and infer decisions already made in code:

| Signal                                                                  | Charter section                                                               |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `pyproject.toml`, `package.json`, `go.mod`                              | tech-stack § Languages & Runtimes, § Frameworks                               |
| `docker-compose.yml`                                                    | tech-stack § Data Stores, § Infrastructure; development § Running the Project |
| `.github/workflows/`, `.gitlab-ci.yml`                                  | development § CI/CD                                                           |
| Linter config (`ruff.toml`, `.eslintrc*`, `pyproject.toml [tool.ruff]`) | development § Linting & Formatting                                            |
| Test config (`pytest.ini`, `conftest.py`, `jest.config.*`)              | development § Testing                                                         |
| `.pre-commit-config.yaml`                                               | development § Linting & Formatting, § CI/CD                                   |

### Step 2 — Create the skeleton and pre-populate

Create the three files from templates (as in `--init` Step 1), then replace
`To be decided.` with what the scan found, wherever a signal maps cleanly
to a section. Leave sections with no signal as `To be decided.`

### Step 3 — Present for confirmation

Summarise the findings as a single list and ask the stakeholder to confirm,
correct, or extend it — e.g. *"I found Python 3.11, FastAPI, PostgreSQL,
ruff, pytest, GitHub Actions. Confirm, correct, or add what I missed."*
Update the affected sections with the stakeholder's corrections before
moving on.

After confirming test-related findings, invoke `detect-test-regime` to
produce the full multi-suite `docs/charter/testing.yaml`. Once it returns
and the user has seen the discovered suites, `detect-test-regime` asks
about the testing strategy document — verify that `testing_strategy:` is
populated before proceeding.

**No Epic 0 derivation in this mode** — the mise en place already exists in
the scanned codebase.

### Step 4 — Validate and format

Same as `--init` Step 3: `factory/scripts/charter-lint`, then
`factory/scripts/mdformat --number` on each changed file.

### Step 5 — Commit

```
docs: scaffold project charter from codebase scan (--init --scan)
```

**Completion**: all three charter files exist, populated from scan findings
where signals existed, stakeholder has confirmed or corrected every
finding, `charter-lint` (default mode) passes.

## Mode 3 — completeness sweep (no flag)

Runs once, before the planning gate, after architecture has settled enough
that most tech-stack and development decisions are known.

### Step 1 — Walk every "To be decided" entry

Read all three charter files. For each section still reading `To be decided.`, ask the stakeholder to decide it now. A decision is either:

- a concrete answer (record it in the section, replacing the placeholder), or
- an **explicit deferral** — the stakeholder chooses not to decide yet. Record
  the deferral as prose stating that, not as a bare `To be decided.` (e.g.
  "Deferred — no caching layer needed until read load requires one.").

House-rules entries may stay genuinely undecided past this sweep (the
planning gate does not block on them); tech-stack and development entries
must reach one of the two states above, because `charter-lint --planning-gate` will reject a literal `To be decided.` in those two files.

After walking the charter files, check `docs/charter/testing.yaml`. If it
is missing or empty, invoke `detect-test-regime`. If `testing_strategy:` is
not yet populated, ask the user: *"Does this project have a testing
strategy document? If so, where is it?"* Record the answer in
`docs/charter/testing.yaml` — default to
`factory/rulebooks/conventions/testing-strategy.md` if the project has
none. The planning gate needs this field.

### Step 2 — Check for existing artifacts, derive Epic 0

For each concrete decision that implies a file, configuration, or
infrastructure artifact, check whether that artifact already exists in the
repository.

| Charter decision                   | If missing                                                                                                   | If exists                                              |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------ |
| Language/framework choice          | Story: initialize the manifest (`pyproject.toml`, `package.json`, …) with core dependencies and version pins | No story, or a "verify versions match charter" story   |
| Test framework choice              | Story: set up the test harness — config, directory structure, run command                                    | No story                                               |
| Linter/formatter/pre-commit choice | Story: configure linter, formatter, and pre-commit hooks                                                     | No story, or a "verify config matches charter" story   |
| Data store choice                  | Story: create the compose/infra file wiring the chosen data stores                                           | No story, or a "verify topology matches charter" story |
| CI/CD choice                       | Story: create the CI pipeline — lint, test, build stages                                                     | No story                                               |
| Repository layout choice           | Story: scaffold the directory structure                                                                      | No story                                               |

The stakeholder can point at existing work instead of a fresh story — "use
this pre-commit config I prepared," "adapt this Makefile from the other
project" — in which case write the smaller "verify/adapt" story, not the
full setup story.

### Step 3 — Write Epic 0 stories

For each derived story, write `backlog/ST-NNNN.md` in the standard story
format (see [story.md template](../../rulebooks/templates/story.md)):

- `epic: "Epic 0 — Project Setup"`
- `tier: economy`
- `status: pending`
- MoSCoW: `**Priority:** must-have`
- `traces:` left empty — the epic label is sufficient identification
- `outputs:` the concrete file(s) the story produces
- Acceptance criteria describe setup verification, not behaviour (e.g.
  "`pyproject.toml` exists with pinned dependencies and `pip install -e .`
  succeeds")

Use the lowest available `ST-NNNN` numbers — read `backlog/` for the next
free id, starting from `ST-0001` if the backlog is empty.

### Step 4 — Write the final "update development.md" story

Always create one closing story, regardless of how many other Epic 0
stories exist:

- Title: "Update development.md with actual commands and paths"
- `epic: "Epic 0 — Project Setup"`, `tier: economy`, MoSCoW `must-have`
- `deps:` every other Epic 0 story id written in Step 3
- Acceptance criteria: `docs/charter/development.md` reflects the actual
  commands, paths, and topology produced by the rest of Epic 0 — not the
  decisions recorded pre-Epic-0

This story sequences last: it cannot be done until the setup work it
describes exists. Once it is done, `development.md` is fact, not intent.

If Step 3 produced zero stories (every artifact already existed), still
write this closing story — house-rules and tech-stack decisions may still
need reflecting into development.md once the stakeholder's deferrals and
confirmations from Step 1 are final.

### Step 5 — Validate and format

Run `factory/scripts/charter-lint --planning-gate` — confirms tech-stack
and development carry no remaining `To be decided.` (house-rules may still
have some). Run `factory/scripts/backlog-lint --backlog-dir backlog` over
the new Epic 0 stories — confirms schema and acyclic `deps`. Fix any
finding before proceeding. Format every changed or created file with
`factory/scripts/mdformat --number <path>`.

### Step 6 — Present for approval

Present the completed charter and the full Epic 0 batch together. Ask the
stakeholder to approve both as one gate: *"These are the decisions, this is
the setup work they imply — begin?"* This is the planning gate; planning
does not start until this approval and `charter-lint --planning-gate` both
pass.

### Step 7 — Commit

```
docs: complete project charter — completeness sweep
```

for the charter edits, and one commit per Epic 0 story (or a single batch
commit listing every `ST-NNNN` id touched) for the backlog files, per
[commit-conventions.md](../../rulebooks/conventions/commit-conventions.md).

**Completion**: no `To be decided.` remains in tech-stack.md or
development.md (deferrals are recorded as explicit prose instead),
`charter-lint --planning-gate` passes, every missing artifact has a
corresponding Epic 0 story, the closing "update development.md" story
exists and depends on every other Epic 0 story, `backlog-lint` passes,
stakeholder has approved charter and Epic 0 together.

## Validation reference

| Script                                               | Mode                    | Checks                                                                       |
| ---------------------------------------------------- | ----------------------- | ---------------------------------------------------------------------------- |
| `factory/scripts/charter-lint`                       | default (all modes)     | files exist, required sections present, no section empty, frontmatter parses |
| `factory/scripts/charter-lint --planning-gate`       | completeness sweep only | default checks, plus no `To be decided.` in tech-stack/development           |
| `factory/scripts/backlog-lint --backlog-dir backlog` | completeness sweep only | Epic 0 story schema and `deps` acyclicity                                    |

`validate` runs `charter-lint` automatically once `docs/charter/` exists —
invoking it here is a courtesy check during the interactive session, not a
replacement for that gate.
