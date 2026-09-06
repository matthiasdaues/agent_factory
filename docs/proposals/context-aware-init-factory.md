---
schema_version: 2
title: Context-Aware Init-Factory
status: open
owner: md@matthiasdaues.de
created: 2026-09-04
updated: 2026-09-06
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

## Open questions — resolved

1. **Where does the scan output go?** → `config/project-context.json`
   (new file). `project.json` is identity (stable UUID, name);
   `project-context.json` is observation (changes as the project evolves).
   Different lifecycles, different files. The fitting state lives in the
   same file as a `fitting` key — it is part of the project's context, not
   a separate runtime artifact.

2. **Selective CLI wiring — part of this proposal?** → Yes.
   **Implemented.** `--cli` accepts multiple values, interactive
   multi-select, `_wants()` gating. Committed and tested.

3. **How does the context interact with the charter?** →
   `project-context.json` is a pre-charter artifact. It feeds into
   capture-charter's `--scan` mode as a starting point (confirmed
   observations, not raw signals). capture-charter enriches it with
   AI-assisted interpretation. The context file names what was *observed*;
   the charter says what it *means*.

4. **Dependency parsing depth?** → Shallow parse of top-level manifest
   dependencies (`pyproject.toml` `[project.dependencies]`,
   `package.json` `dependencies`), matched against a hardcoded
   known-framework list. No transitive crawl. `tomllib` (stdlib 3.11+)
   for TOML, `json` for JSON. Still deterministic, still fast.

5. **Monorepo multi-stack?** → Flat list with evidence paths. If the scan
   finds `pyproject.toml` at root and `apps/frontend/package.json` in a
   subdirectory, both appear as observations with their paths as evidence.
   VIRGIL interprets the pattern ("Is this a monorepo with separate
   stacks?") during the confirmation step.

6. **"What do you want" at init time?** → No. Init fingerprints silently.
   The session entrypoint (VIRGIL) routes intelligently based on the
   fingerprint. CLI selection is the only interactive question at init
   time. Progressive disclosure wins — ask "what do you want" only after
   the user has seen what exists.

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

**The surface area is intimidating.** 17 agents, 58 skills, 11 playbooks,
102 scripts. The root README is polished and well-structured, but it links
to a beginner's intro that references a deprecated flow, a factory README
that's 160 lines of dense setup prose, and a 700-line factory guide. A
developer who just wants to try this needs to read a lot before they do
anything.

**init-factory is a 2,340-line Python script.** It does its job —
idempotent, reversible, well-documented — but it's a wall. It wires up
four CLI ecosystems (Claude Code, Copilot, Pi, Codex) whether you use them
or not. It creates symlinks into `.claude/`, `.github/`, `.pi/`, `.codex/`
all at once. Most users use one or two CLIs. The rest is noise in their
project tree.

**The onboarding path has too many forks too early.** Session entrypoint:
four options. Option B expands into eight sub-options. Option C lists all
agents or all playbooks. A newcomer doesn't know enough to choose. VIRGIL
is now the default session persona from the start (commit `2804a1b`), and
the newcomer-tour exists, but they activate only after init-factory has
already dropped 50+ files into the project and the user has opened a CLI
session. The "show me around" moment comes after the commitment, not before
it.

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
  drops 50+ files, the 2,340-line script does everything at once.
- **Mental onboarding** — the path from "what is this" to "I know what to
  do next." Too many forks too early, the good guide is buried, the README
  explains machinery before motivation.
- **Factory distribution** — the repo conflates the installable toolset
  with its own development history. Consumers see 200 stories, 119 findings,
  and 39 proposals that aren't theirs.

They stay in one proposal because init-factory is where all three converge —
the moment the technical wiring happens, the mental model forms, and the
distribution boundary matters.

## Proposed path — the fitting (2026-09-06, replaces four-layer sketch)

The earlier four-layer sketch (Layer 0–3) described what the user sees at
each stage. This revision describes the *states* the project-factory
relationship moves through and what drives each transition. The user
experience falls out of the states, not the other way around.

The metaphor is a dressmaker's fitting. The factory brings the craft; the
project brings the shape. Neither is incomplete without the other — the
fitting is where they meet. And unlike a meld or a graft, the result is
separable: `remove-factory` takes the factory off and the project stands on
its own, unchanged.

### The lifecycle

```
Greenfield:   init ──────────────────────────────► fitted
Brownfield:   init ──► unfitted ──► fitting ──► fitted
```

| State        | What exists                                                        | Factory knows the project? | Project reflects the factory? |
| ------------ | ------------------------------------------------------------------ | -------------------------- | ----------------------------- |
| **init**     | `factory/`, selected CLIs wired, pre-commit if absent              | No                         | No                            |
| **unfitted** | Code, tests, CI — a real project the factory just met              | No                         | No                            |
| **fitting**  | Partial agent-context, some hooks, fingerprint partial             | Partially                  | Partially                     |
| **fitted**   | Full agent-context, hooks wired or declined, fingerprint confirmed | Yes                        | Yes                           |

**Greenfield** skips unfitted and fitting. There is no pre-existing project
to learn about, so init produces an empty project that the first playbook
(charter, spec, architecture) shapes from scratch. The project is born
fitted — the factory's understanding and the project's configuration grow
together.

**Brownfield** walks through all four states. The project has its own
conventions, stack, test runner, CI, maybe docs. The factory is the
newcomer. Until the fitting is complete, every session should surface the
offer: "I don't fully know your project yet. Want to continue the fitting?"

### init — mechanical, minimal, selected CLIs

`init-factory --cli claude copilot` (or auto-detect from cwd, or
interactive multi-select). Installs for the selected CLIs only. Ships
everything — agents, skills, playbooks, scripts — but wires up only the
chosen ecosystems. No questions beyond the project name and CLI selection.

What init does:

- Copy `factory/` into the project.
- Wire up the selected CLIs' dot-directories (`.claude/`, `.github/`,
  `.pi/`, `.codex/`). Only the chosen ones — not all four.
- Create `config/project.json` (name, UUID).
- Create `.pre-commit-config.yaml` with factory hooks if no config exists.
  If a pre-commit config already exists, defer hook merging to the fitting.
- Print a sectioned receipt: what was created, how to undo.

What init does NOT do:

- Merge into an existing `.pre-commit-config.yaml` (that belongs in the
  fitting, where the user can review each hook).
- Run a mechanical fingerprint (that belongs in the first session, where
  VIRGIL can present and confirm it).
- Reformat the user's files.
- Create agent-context, reading guides, or any doc structure.

Adding CLIs later: `init-factory --cli copilot`. Additive, not
destructive.

Success moment: *"That was painless."*

### unfitted → fitting — VIRGIL opens the conversation

First session after init. VIRGIL detects no agent-context
(`docs/agent-context/` absent or empty) and no project fingerprint
(`config/project-profile.json` absent). Instead of the A/B/C/D menu,
VIRGIL opens with one recommendation:

- Existing codebase, no agent context → "I just met your project. Want to
  do a quick fitting? Five questions, and I'll know how to help."
- Empty project → "Nothing here yet. Want to try a quick spike, or start
  building something real?" (This is the greenfield path — init → fitted.)

The full menu exists as a fallback ("show me all options"), not as the
default.

The fitting is conversational and incremental. VIRGIL:

1. Runs the mechanical fingerprint (language, test runner, CI, package
   manager, linter). Presents findings: "I see Python 3.12, pytest, GitHub
   Actions, ruff. Correct?" Writes confirmed findings to
   `config/project-profile.json`.
2. Walks through the agent-context interview (capture-context), one concern
   at a time. Each confirmed key is written immediately — partial progress
   is saved, and the user can stop and resume across sessions.
3. Offers hooks: "Want me to add pre-commit hooks for markdown formatting
   and link checking?" Yes wires them; no records the decision so the offer
   doesn't repeat.
4. Surfaces the factory guide's relevant section when the user hits a
   concept for the first time. No catalogue upfront. 58 skills, 17 agents,
   11 playbooks stay invisible until the user's path reaches them.

The fitting persists across sessions. Each session, VIRGIL checks what's
still missing and offers to continue — not as a blocker, but as a standing
offer the user can defer.

### fitted — the offer stops

The transition from fitting to fitted happens when:

- Agent-context index files have at least one non-deferred key each, or
  the user has explicitly deferred all remaining keys.
- The project fingerprint exists and has been confirmed.
- Hooks have been installed or explicitly declined.
- VIRGIL asks "I think I know enough. Anything else?" and the user
  confirms.

A marker records the fitted state. The "want to continue the fitting?"
offer stops. Sessions open with "What do you want to work on?" — the
factory knows the project's shape.

Success moment: *"I didn't have to learn the whole thing to get value from
it. It learned me."*

### The README (orthogonal to the lifecycle)

The README is the only pre-commitment surface. It has 30 seconds.

- What problem this solves (one paragraph, one before/after).
- "Try it — one command removes everything" (reversibility as trust signal,
  not a footnote).
- One command to run poc-spike against a scratch directory, no full
  installation required.

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

### What changed from the four-layer sketch

- Layers 1–3 collapsed into a lifecycle with named states. The user
  experience is the same — minimal init, conversational onboarding,
  progressive depth — but the model is state-driven, not layer-driven.
  States are observable and testable; layers were conceptual.
- Pre-commit hooks: greenfield (no config) → init creates with factory
  hooks. Brownfield (config exists) → fitting handles the merge.
- The mechanical fingerprint runs at init time (deterministic, no AI).
  VIRGIL presents and confirms it at first session — interpretation
  belongs to the session, not the installer.
- The fitted marker lives in `config/project-context.json` alongside the
  scan results. One file, one place to look.
- The README concern is separated out — it's a presentation problem, not a
  lifecycle state. The distribution concern is moot: consumers run
  `init-factory` against their own project and never browse the source
  repo.

### `_scan_project_context` specification

Deterministic project scan, added to init-factory. Runs after factory copy
and CLI wiring. Writes `config/project-context.json`.

**Walk rules.** Recursive from the target directory. Skip directories
named: `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`, `.tox`,
`.nox`, `dist`, `build`, `.eggs`, `.mypy_cache`, `.pytest_cache`,
`.ruff_cache`, `factory` (the just-installed copy). Follow no symlinks.

**Evidence model.** Every observation is `{"name": "...", "evidence": "relative/path"}`. The evidence path is the file that triggered the
detection, relative to the target root. VIRGIL uses it for confirmation:
"I see Python because of `pyproject.toml`."

**Detection categories:**

| Category           | Signals                                                                                                                                                                                                           |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `languages`        | Manifest files: `pyproject.toml` → python, `package.json` → javascript, `tsconfig.json` → typescript, `go.mod` → go, `Cargo.toml` → rust, `pom.xml`/`build.gradle` → java, `Gemfile` → ruby                       |
| `package_managers` | Lockfiles: `uv.lock` → uv, `poetry.lock` → poetry, `Pipfile.lock` → pipenv, `requirements.txt` → pip, `package-lock.json` → npm, `yarn.lock` → yarn, `pnpm-lock.yaml` → pnpm, `go.sum` → go, `Cargo.lock` → cargo |
| `frameworks`       | Shallow parse of top-level manifest dependencies against a hardcoded known-framework list (fastapi, django, flask, express, next, react, vue, angular, gin, actix-web, spring, rails, etc.)                       |
| `ci`               | Config dirs/files: `.github/workflows/` → github-actions, `.gitlab-ci.yml` → gitlab-ci, `Jenkinsfile` → jenkins, `.circleci/` → circleci, `bitbucket-pipelines.yml` → bitbucket                                   |
| `linters`          | Config files: `ruff.toml` or `[tool.ruff]` → ruff, `.eslintrc*`/`eslint.config.*` → eslint, `.prettierrc*` → prettier, `biome.json` → biome, `.rubocop.yml` → rubocop                                             |
| `test_runners`     | Config/conventions: `conftest.py`/`pytest.ini`/`[tool.pytest]` → pytest, `jest.config.*` → jest, `vitest.config.*` → vitest, `*_test.go` files → go-test                                                          |
| `docs_tooling`     | Config files: `mkdocs.yml` → mkdocs, `conf.py` → sphinx, `docusaurus.config.*` → docusaurus                                                                                                                       |
| `docs_structure`   | Presence: `README.md`, `docs/`, `CHANGELOG.md`                                                                                                                                                                    |

**Framework list** (hardcoded, initial set):

Python: `fastapi`, `django`, `flask`, `starlette`, `celery`, `sqlalchemy`
JavaScript/TypeScript: `express`, `next`, `react`, `vue`, `angular`,
`svelte`, `nuxt`, `nest`, `hono`
Go: `gin`, `echo`, `fiber`
Rust: `actix-web`, `axum`, `rocket`
Java: `spring-boot`, `spring`
Ruby: `rails`, `sinatra`

**Fitting state** (written by init, updated by VIRGIL):

```json
{
  "fitting": {
    "status": "unfitted",
    "fingerprint_confirmed": false,
    "agent_context_populated": false,
    "hooks_decided": false
  }
}
```

**Not in scope for this scan** (left for VIRGIL / skills):

- Data stores from docker-compose (too interpretive)
- Architecture style (needs code reading)
- Multi-suite test strategy (handled by detect-test-regime skill)
- Transitive dependency analysis

## Documentation gaps — newcomer path audit (2026-09-06)

Tracing the newcomer journey from first contact (root README) through setup
(factory README) to reference (factory guide). Each gap is something a
newcomer encounters but cannot learn about from the documentation.

### 1. Model matrix (`config/model.conf`)

The file exists after install. The `matrix-lint` hook validates it. The
orchestrator README says "model is resolved from `config/model.conf` based on
the agent's tier." No doc explains:

- What it is (maps agent tiers to AI models, per CLI)
- What tiers are (economy / standard / strong) and which agents use which
- The `cli.tier = model-id` format
- How to customize it for your own CLI or models
- What `on_missing = halt` does

Not mentioned in the factory README or the factory guide at all.

### 2. Tiers

The concept behind the model matrix. No user-facing doc defines what
economy/standard/strong means, which agents use which tier, or how tier
relates to cost. The word "tier" never appears in the factory guide except
buried in the usage-capture section.

### 3. Stale ruff references in factory guide

Five mentions (lines 555, 561, 575, 587, 688) still describe ruff as a
built-in hook. Ruff was removed from both the pre-commit template and the
source repo config (commit `a210970`). The guide contradicts reality.

### 4. `config/project.json`

Appears in the factory README reference table and the guide's usage-capture
section. No explanation of what it does or whether the user should care.

### 5. Factory directory layout

After install, the user has `factory/` containing agents/, skills/,
playbooks/, rulebooks/, scripts/, config/, docs/, fixtures/, reports/. No
map. The factory README says "The script copies a `factory/` directory" and
stops. The guide introduces each concept but never shows the directory tree.

### 6. Factory README "How it works" section

Just a bullet list linking to the guide. Omits agent context, model matrix,
and config/ entirely. A newcomer who reads only the README misses that these
exist.

### 7. Agent context not mentioned in factory README

The root README mentions it. The factory guide has a full section. But the
factory README — the setup doc where a newcomer goes after cloning — never
mentions it. The newcomer following the install path won't know it exists
until VIRGIL asks about it in a session.

### 8. Agent context creation timing

The guide says "`docs/agent-context/` is a routing switchboard" but never
says when it gets created. A newcomer looking for it after `init-factory`
won't find it — it's created during onboarding (greenfield/brownfield
playbooks), not at install time.

## Baseline update (2026-09-06)

Work done since this proposal was drafted. Updates the starting point for
the fitting lifecycle.

### Documentation editorial pass

- **`92449e8`** — Switched "operator" wording to "user" across 127 files.
- **`d5dffa0`** — Editorial pass over all 58 skills. Cut bureaucratic
  openers ("This skill provides a capability to…"), removed redundant
  footers, fixed verb agreement. 8 skills rewritten.
- **`f5deffe`** — Rewrote pre-commit hook comments for clarity. Each hook
  now has a two-line comment explaining what it checks and why.
- **`a210970`** — Removed ruff from the pre-commit template and annotated
  the remaining hooks. The factory guide still has five stale ruff
  references (gap 3 above — not yet fixed).

### VIRGIL as default session persona

- **`2804a1b`** — VIRGIL is now adopted at the start of every session, not
  only when option D is chosen. The session entrypoint in AGENTS.md reads
  the virgil agent definition and adopts its role before presenting the
  menu. The factory guide introduces VIRGIL in "Your very first session"
  with the Dante/Purgatory allusion and J.A.R.V.I.S. comparison.
- This is the foundation for the **unfitted → fitting** transition — VIRGIL
  is the default voice but does not yet read a project fingerprint or offer
  a tailored recommendation. The A/B/C/D menu is still the default, not a
  fallback.

### Pre-commit merge bug fixed

- **`2d8ff9c`** — Three bugs in the init-factory / merge-precommit-config
  pipeline:
  1. `_tools_in_target` matched `factory/scripts/mdformat` in the dev
     repo's development section, triggering the dedup filter and silently
     dropping the factory's mdformat hook. Fixed: entries using
     `factory/scripts/` are excluded from the dedup check.
  2. If `_strip_factory_block` failed silently, the merge would splice a
     new copy on top of the old one, duplicating the entire block. Fixed:
     post-strip marker check raises instead of splicing.
  3. `handle_precommit` ran `merge-precommit-config` even when
     `.pre-commit-config.yaml` was git-tracked. In the dev repo this
     overwrote intentional differences (bare entries, source-repo paths,
     extra excludes) with the consumer template. Fixed: skip merge when the
     file is git-tracked.
- New test suite: `tests/factory/test_merge_precommit_config.py` (9 tests).

### Monorepo restructure

- **`eb22486`** — Product source moved to `packages/factory/`. Root
  `init-factory` is a thin wrapper. `factory/` at root is the installed
  copy (git-ignored), synced by `update-factory`.

### What this changes for the proposal

The editorial pass addressed the *tone* half of the mental-onboarding
concern — skills read clearly, hooks explain themselves, the language is
"user" not "operator." The *structure* half — too many forks, the guide is
buried, the README leads with machinery — is untouched.

VIRGIL as default persona is the foundation for Layer 2 but not yet the
thing itself. The four-option menu is still the first thing a user sees.
The fingerprint-driven recommendation ("I see Python/FastAPI, you probably
want…") does not exist yet.

The pre-commit fix removes a friction point from the developer experience
but does not advance any proposal layer directly.

**Doc gaps status (updated 2026-09-06):**

| #   | Gap                               | Status |
| --- | --------------------------------- | ------ |
| 1   | Model matrix docs                 | Closed |
| 2   | Tier definitions                  | Closed |
| 3   | Stale ruff refs in guide          | Closed |
| 4   | `config/project.json` unexplained | Closed |
| 5   | Factory directory layout          | Closed |
| 6   | Factory README "How it works"     | Closed |
| 7   | Agent context in factory README   | Closed |
| 8   | Agent context creation timing     | Closed |
