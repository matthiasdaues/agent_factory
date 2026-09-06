---
schema_version: 2
title: Context-Aware Init-Factory
status: draft
owner: md@matthiasdaues.de
created: 2026-09-04
updated: 2026-09-04
supersedes:

impact:
  scope: tbd
  architecture_change: tbd
  external_contract_change: tbd
  boundaries: []

governance:
  assurance: tbd
  risk_domains: []

estimate:
  as_of: 2026-09-04
  basis: judgment
  confidence: low
  human_review_hours:
    min: 0
    max: 0
  normalized_tokens:
    min: 0
    max: 0
---

# Context-Aware Init-Factory — Collected Evidence and Design Seeds

Raw material for a future structured proposal. Everything below is evidence
gathered from the codebase, not yet refined into design decisions.

## The core idea

Make init-factory aware of what is already there in the target project, which
language stack is used, and what the user/project wants from the factory.
Today init-factory operates nearly context-blind — it wires up symlinks,
hooks, and config without understanding the project it is entering. The
project's character is discovered much later (brownfield Phase 5.3, or
greenfield Phase 1 charter capture). Pulling that awareness forward into
init-factory would let the factory greet a project on its own terms from the
first moment.

## What init-factory already detects (as of 2026-09-04)

All detection lives in `factory/scripts/init-factory`:

1. **Test regime** (`_scan_test_entrypoints`, line 1743): scans Makefile,
   package.json, tox, nox, Justfile, Taskfile, pytest config. Records
   `test_command` in `docs/charter/testing.yaml` when exactly one
   unambiguous match is found. Multiple matches → gap surfaced, nothing
   written. Existing `testing.yaml` → left untouched.

2. **Project identity** (line 1620): asks for a project name interactively
   (or via `--project-name`), generates a stable UUID, writes
   `config/project.json`. Consumed by usage capture.

3. **Pre-existing orientation files**: detects `.claude/CLAUDE.md`,
   `.github/copilot-instructions.md`, `AGENTS.md` as real files (not
   symlinks). Prepends a marker-fenced orientation block instead of
   overwriting. Project content preserved below the block.

4. **Pre-existing `.pre-commit-config.yaml`**: delegates to
   `merge-precommit-config` to splice Agent Factory hooks alongside the
   project's own hooks without disturbing them.

5. **Dangling `origin/HEAD`** (commit `cb6aa1f`, BR-050): best-effort
   repair via `git remote set-head origin --auto`, falling back to local
   ref scan.

6. **Existing `config/model.conf`**: left untouched (BR-022).

7. **Existing `factory/` directory**: skipped entirely (Extension 3a) —
   refreshing is `update-factory`'s job.

That is everything. No language detection, no framework fingerprinting, no
CI/CD identification, no "what do you want from the factory" interaction.

## Where the missing detection already exists

### capture-charter `--init --scan` (Mode 2)

`factory/skills/capture-charter/SKILL.md` Step 1 has a full detection table:

| Signal                                                                  | Charter section                                                               |
| ----------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `pyproject.toml`, `package.json`, `go.mod`                              | tech-stack § Languages & Runtimes, § Frameworks                               |
| `docker-compose.yml`                                                    | tech-stack § Data Stores, § Infrastructure; development § Running the Project |
| `.github/workflows/`, `.gitlab-ci.yml`                                  | development § CI/CD                                                           |
| Linter config (`ruff.toml`, `.eslintrc*`, `pyproject.toml [tool.ruff]`) | development § Linting & Formatting                                            |
| Test config (`pytest.ini`, `conftest.py`, `jest.config.*`)              | development § Testing                                                         |
| `.pre-commit-config.yaml`                                               | development § Linting & Formatting, § CI/CD                                   |

This runs in brownfield Phase 5.3 — after architecture extraction, after
ATAM review. It requires AI in the loop (it reads configs, infers meaning,
asks the stakeholder to confirm). It produces `docs/charter/tech-stack.md`,
`docs/charter/development.md`, `docs/charter/house-rules.md`.

**Key tension**: capture-charter's scan is conversational and interpretive.
init-factory is deterministic and AI-free. Pulling the scan forward means
deciding which signals can be read mechanically (file presence, manifest
parsing) versus which need interpretation (framework inference from
dependency lists, CI pipeline analysis).

### detect-test-regime skill

`factory/skills/detect-test-regime/SKILL.md` — the AI-augmented version of
init-factory's `_scan_test_entrypoints`. Handles multiple test suites,
discovers testing strategy documents, populates the full
`docs/charter/testing.yaml` with multi-suite entries and strategy reference.
init-factory carries the deterministic subset; the skill carries the
interpretive superset.

This is the existing model for "deterministic core in init-factory,
interpretive extension in a skill." The same pattern could apply to
language-stack detection, CI detection, etc.

## Explicitly deferred items from prior proposals

### Newcomer onboarding proposal (accepted 2026-08-28)

`docs/proposals/newcomer-onboarding-and-incremental-brownfield.md` deferred:

- **Automatic newcomer detection**: checking for artifacts (a completed
  spike, a charter, prior playbook outputs) to offer the guided tour
  proactively. Currently the tour is a menu choice.
- **Feature-addition ceremony scaling by change size**: incremental
  deepening is a natural consequence, not a ceremony reduction.
- **User profiles or cross-project memory of who has used the factory
  before.**
- **Changes to the orchestrator or automatic mode.**

The first and third items are directly relevant — they envision init-factory
or the session entrypoint knowing something about the user and the project's
history with the factory.

### UC-08 (archived spec)

`docs/~archive/spec/use_cases/UC-08-initialize-agent-factory-into-a-project.md`
— the original use case. Step 11 is the test-regime scan (BR-030). No
mention of broader detection. The acceptance criteria test idempotency,
collision handling, test-regime detection, and `origin/HEAD` repair. Nothing
about project awareness beyond test setup.

## The gap — what init-factory could detect but doesn't

| What                                        | Mechanically detectable?            | Where capability exists today      |
| ------------------------------------------- | ----------------------------------- | ---------------------------------- |
| Primary language (Python, Node, Go, Rust…)  | Yes — manifest file presence        | capture-charter scan table         |
| Framework (FastAPI, Express, Gin…)          | Partially — dependency list parsing | capture-charter scan (AI-assisted) |
| Package manager (pip/uv, npm/yarn/pnpm, go) | Yes — lockfile presence             | Nowhere explicit                   |
| CI/CD platform (GH Actions, GitLab CI)      | Yes — config dir/file presence      | capture-charter scan table         |
| Data stores (Postgres, Redis…)              | Partially — docker-compose parsing  | capture-charter scan (AI-assisted) |
| Existing docs structure                     | Yes — directory/file presence       | Nowhere                            |
| Existing test infrastructure                | Yes (single), partially (multi)     | init-factory + detect-test-regime  |
| Linter/formatter setup                      | Yes — config file presence          | capture-charter scan table         |
| What user wants from factory                | No — requires interaction           | Implicit in playbook choice        |
| User's prior factory experience             | No — requires memory/profile        | Deferred in newcomer proposal      |

## Design seeds — possible directions

### Direction A: Deterministic project fingerprint at init time

Extend `_scan_test_entrypoints` pattern. Add a `_scan_project_stack`
function that reads manifests and config files to produce a
`config/project-profile.json` alongside the existing `config/project.json`:

```json
{
  "languages": ["python"],
  "package_managers": ["uv"],
  "frameworks": ["fastapi"],
  "ci": "github-actions",
  "linters": ["ruff"],
  "formatters": ["ruff-format"],
  "test_runners": ["pytest"],
  "data_stores": [],
  "docs_structure": {
    "has_readme": true,
    "has_docs_dir": false,
    "has_context_md": false
  }
}
```

Fully deterministic, no AI. Runs as part of init-factory. Downstream
skills and agents read this profile to tailor their behavior. capture-charter
`--scan` can start from this instead of re-scanning from scratch.

**Pro**: consistent with init-factory's design (no AI, idempotent,
deterministic). Gives every later step a head start.

**Con**: mechanical detection is shallow — knows "has FastAPI dependency" but
not "this is a REST API with 47 endpoints." The interpretive layer still
needs capture-charter or reverse-map.

### Direction B: Interactive "what do you want" at init time

After the mechanical scan, init-factory presents its findings and asks:

- "I found Python/FastAPI/pytest/ruff/GitHub Actions. Correct?"
- "What do you want from the factory?" (options: just guardrails, full
  development workflow, research tooling, brownfield documentation)
- "Which CLIs will you use?" (Claude Code, Copilot, Pi, Codex — currently
  all four are always wired)

This shifts init-factory from "install everything, figure out later" to
"install what makes sense." Selective installation reduces noise in projects
that only want, say, the guardrails and not the full playbook machinery.

**Pro**: factory meets the project where it is. Reduces the wall-of-content
problem the newcomer proposal identified.

**Con**: breaks init-factory's current "no interaction beyond project name"
simplicity. Adds decision points before the user knows enough to decide.
Conflicts with the "progressive disclosure" principle — how do you ask
"what do you want" before the user knows what's available?

### Direction C: Post-init profile skill (AI-assisted)

Keep init-factory deterministic and minimal. Add a new skill
(`profile-project` or extend capture-charter) that runs after init, reads
the mechanical scan, and produces a richer profile through AI-assisted
interpretation. This profile feeds into the session entrypoint, tailoring
which options are highlighted.

**Pro**: cleanest separation of concerns. init-factory stays simple.
AI-assisted interpretation lives where it belongs (in a skill).

**Con**: the profile step is easily skipped. The session entrypoint can't
tailor itself if the user never ran the profile skill.

### Direction D: Combine A and C — mechanical fingerprint at init, interpretive enrichment on demand

init-factory produces `config/project-profile.json` mechanically. The
session entrypoint reads it (if present) and adjusts recommendations. A
`profile-project` skill enriches the profile with AI-assisted analysis when
the user or a playbook invokes it. capture-charter `--scan` consumes the
profile as a starting point rather than scanning from scratch.

This follows the existing detect-test-regime pattern:
deterministic core in init-factory, interpretive extension in a skill.

## What the profile could influence

If init-factory produces a project profile, downstream consumers could use
it:

- **Session entrypoint**: "I see this is a Python/FastAPI project with
  pytest and GitHub Actions. Option B.1c (greenfield) probably isn't what
  you need — you likely want B.3a (add a feature) or B.2 (brownfield
  onboarding)."
- **capture-charter `--scan`**: skip re-scanning what init-factory already
  found. Start from the profile and ask for confirmation/enrichment.
- **detect-test-regime**: already partly done — init-factory's test scan
  seeds `testing.yaml`, the skill enriches it.
- **Selective CLI wiring**: if the user says "I only use Claude Code," skip
  `.github/`, `.pi/` wiring entirely.
- **Playbook recommendations**: a Python project with no tests might get
  "consider running detect-test-regime before your first feature-addition."
- **Agent behavior**: agents reading the profile could adjust their
  vocabulary, examples, and assumptions to the project's stack.

## Relationship to existing proposals and work

- **Newcomer onboarding** (accepted): this proposal picks up the deferred
  items (automatic detection, user profiles) and grounds them in a concrete
  mechanism.
- **Orchestrator-consumer integration** (accepted): touches init-factory's
  distribution but not its awareness. Orthogonal.
- **UC-08** (archived): would need updating if init-factory gains new steps.
  The activity diagram, acceptance criteria, and business rules would grow.
- **capture-charter**: the main consumer of a richer init. The `--scan`
  mode would shift from full-scan to confirm-and-enrich.
- **detect-test-regime**: the existing precedent for the
  "deterministic core + interpretive skill" split.

## Open questions (genuinely undecided)

1. Should the mechanical scan produce `config/project-profile.json` (a
   new file) or extend the existing `config/project.json` (which currently
   holds only name and UUID)?

2. Should selective CLI wiring be part of this proposal or a separate one?
   It has different risk characteristics (compatibility, existing tests).

3. How does the profile interact with the charter? Is it a pre-charter
   artifact that feeds into capture-charter, or does it become part of the
   charter itself?

4. Should init-factory's scan cover the project's dependency tree (parse
   `pyproject.toml` `[project.dependencies]`, `package.json`
   `dependencies`) or stay at the manifest-presence level? Depth vs.
   complexity tradeoff.

5. What about monorepos with multiple stacks? The current model assumes one
   project identity. A monorepo might have Python backend + React frontend +
   Go CLI.

6. The "what do you want from the factory" question (Direction B) — is this
   premature at init time? The newcomer proposal's design says progressive
   disclosure; the session entrypoint already handles routing. Maybe init
   should fingerprint silently and the entrypoint should route intelligently.

## Note — How the factory presents itself (2026-09-05)

Opinionated developer's-eye assessment of the repo, structure, init process,
and onboarding as they stand today. Recorded as context for whatever shape
this proposal takes.

**The repo doesn't know what it is to the outside world.** The root is
simultaneously the factory toolset, the factory's own development project,
and a documentation archive. A newcomer clones this and sees `backlog/`,
`docs/proposals/`, `docs/findings/`, `docs/reviews/`, 197 story files, 119
findings, 72 reviews, 39 proposals — none of which are theirs. The thing
they actually want (`factory/`) is one directory among many, sitting next to
`orchestrator/` (not yet operational), `poc/`, `sys/`, and
`session-scratchpad.md`.

**The surface area is intimidating.** 17 agents, 58 skills, 13 playbooks, 48
scripts, 312 markdown docs. The root README is polished and well-structured,
but it links to a beginner's intro that references a deprecated flow, a
factory README that's 160 lines of dense setup prose, and a 700-line factory
guide. A developer who just wants to try this needs to read a lot before they
do anything.

**init-factory is a 2,300-line shell script.** It does its job — idempotent,
reversible, well-documented — but it's a wall. It wires up four CLI
ecosystems (Claude Code, Copilot, Pi, Codex) whether you use them or not. It
creates symlinks into `.claude/`, `.github/`, `.pi/`, `.codex/` all at once.
Most users use one CLI. The rest is noise in their project tree.

**The onboarding path has too many forks too early.** Session entrypoint:
four options. Option B expands into eight sub-options. Option C lists all
agents or all playbooks. A newcomer doesn't know enough to choose. VIRGIL
and the newcomer-tour exist to solve this, but they activate only after
init-factory has already dropped 50+ files into the project and the user has
opened a CLI session. The "show me around" moment comes after the commitment,
not before it.

**The README promises simplicity but the experience delivers complexity.**
"Three commands to get started" — true. But the first commit modifies files
because hooks auto-fix formatting. The factory guide explains this as
expected behavior. That's a red flag to most developers: I ran the installer
and it immediately changed my files.

**Internal project artifacts leak into the consumer story.** `docs/` contains
arc42, ADRs, specs, findings, handoffs — all about Agent Factory itself. When
init-factory copies `factory/` into a consumer project, that's clean. But the
repo the consumer cloned also has `backlog/ST-0001.md` through `ST-0206.md`.
There's no `.gitattributes` marking these as development-only. A consumer
browsing the repo for guidance sees the factory's own 200-story backlog
alongside the documentation meant for them.

**The naming carries cognitive load.** Skills named `create-backlog-epics`,
`create-backlog-write-epics`, `create-backlog-stories`,
`create-backlog-story-slices` — four skills whose names only differ by
suffix. `capture-context` vs `update-context` vs
`agent-context-composition` (a convention, not a skill). `grilling` vs
`grill-me` vs `grill-with-docs`. The taxonomy is precise but not obvious.

**The factory guide is good but buried.** It's the single best document in
the repo — explains concepts clearly, builds from simple to complex. But it
lives at `factory/docs/factory-guide.md`, two levels deep, behind a README
that already told you a lot. By the time someone reaches it they've either
figured things out or given up.

**Bottom line:** The factory is built for power users who already know what
they're doing. The engineering underneath is solid — reversible installation,
deterministic gates, separation of concerns. But the presentation assumes
the reader already understands why they need specialist agents, phase-gated
workflows, and YAML routing interfaces. It explains *how* thoroughly and
*what* precisely, but the *why should I care right now* gets lost in the
volume.

## Three concerns, one proposal (2026-09-05)

The assessment above surfaces three distinct problems that converge at init
time:

- **Technical onboarding** — init-factory wires four CLIs unconditionally,
  drops 50+ files, the 2,300-line script does everything at once.
- **Mental onboarding** — the path from "what is this" to "I know what to
  do next." Too many forks too early, the good guide is buried, the README
  explains machinery before motivation.
- **Factory distribution** — the repo conflates the installable toolset
  with its own development history. Consumers see 200 stories, 119 findings,
  and 39 proposals that aren't theirs.

They stay in one proposal because init-factory is where all three converge —
the moment the technical wiring happens, the mental model forms, and the
distribution boundary matters.

## Proposed path — outside in (2026-09-05, revised after UX critique)

### Layer 0 — One page, one command, one result

The README is the only pre-commitment surface. It has 30 seconds.

- What problem this solves (one paragraph, one before/after).
- "Try it — one command removes everything" (reversibility as trust signal,
  not a footnote).
- One command to run poc-spike against a scratch directory, no full
  installation required.
- Success moment: *"I see what this does."*

The distribution problem is solved here or not at all. The consumer's front
door is the root README, and right now it opens into a construction site.
Two options, pick one:

- **Option A** — The consumer never browses the source repo. The README
  targets them, the development artifacts (`backlog/`, `docs/proposals/`,
  `docs/findings/`) are flagged as internal with a one-line boundary note at
  the top of the repo map. Cheap, honest, good enough.
- **Option B** — The consumer-facing docs live at a separate surface (docs
  site, GitHub Pages, a standalone `docs/getting-started/` that init-factory
  can serve). The root README becomes a contributor README. Clean separation
  but more to maintain.

Option A is probably right until there are actual external users.

### Layer 1 — Minimal installation, no questions

init-factory detects the CLI in use (or takes `--cli claude`). Installs for
that CLI only. Ships everything — agents, skills, playbooks, scripts — but
wires up one ecosystem instead of four. No "guardrails or full workflow"
question. The user hasn't used either yet; they can't choose. Install the
lot, for one CLI, quietly.

The mechanical project fingerprint (language, test runner, CI) happens here,
written to `config/project-profile.json`. Silent. No interaction beyond the
project name.

First commit should not modify the user's files. If hooks auto-fix
formatting on factory-owned files, that happens inside init-factory before
it finishes — not as a surprise on the user's first `git add`.

Success moment: *"That was painless."*

### Layer 2 — First session: one recommendation

VIRGIL reads the project fingerprint. Instead of A/B/C/D, it opens with one
suggestion:

- Empty project, no code → "Want to try a quick spike?"
- Existing codebase, no agent context → "Let me learn about your project.
  Five questions."
- Agent context already set up → "What do you want to work on?"

The full menu exists as a fallback ("show me all options"), not as the
default. The recommendation is the default.

Success moment: *"Something useful just happened."*

### Layer 3 — Progressive depth, pull not push

58 skills, 17 agents, 13 playbooks stay invisible until the user's path
reaches them. No catalogue upfront. The factory guide stays available but
isn't required reading — VIRGIL surfaces the relevant section when the user
hits a concept for the first time.

Agent context, reading guides, the interview — all pull-based. The factory
reveals its depth as you use it, not as a wall of documentation before you
start.

Success moment: *"I didn't have to learn the whole thing to get value from
it."*

### UX critique that shaped this revision

- Layers 0 and 1 of the original sketch were merged. The README *is* the
  zero-commitment contact. Two separate "read before you try" surfaces means
  neither is the canonical one.
- Dropped the "ask questions upfront" approach for Layer 1. Progressive
  installation means installing the minimum and offering expansion later, not
  asking questions the user can't answer yet.
- Added success moments per layer — the path should define what the user
  feels, not just what the system does.
- Uninstall as a trust signal belongs at Layer 0, not buried in the factory
  guide.
- The distribution problem was the hardest of the three and got the least
  concrete treatment in the first sketch. Option A/B framing addresses it
  directly.
