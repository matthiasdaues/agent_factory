# Changelog

## 1.6.0 — 2026-11-06

This release numbers every indexed artifact from one counter on the
project's remote, so two sessions on two branches never take the same ID
(counter-ids, ST-0368 to ST-0375). It also seeds that counter in the
fitting and keeps a local counter until a remote exists (counter-ids-fitting,
ST-0376 to ST-0385). Run `update-factory` to receive it. A project that
already has IDs runs fitting step 4 once, or seeds by hand with
`next-id --seed`.

### Features

- **`next-id` hands out every ID from one counter.** The script claims the
  next number of an ID prefix from the ref `refs/ids/counters` on `origin`,
  with a leased push from a throwaway repository, so the clone stays
  unchanged. A stale lease is retried at most ten times; any other refusal
  fails at once and names its cause. Every git call runs without a prompt and
  stops after 30 seconds. `--seed` creates the counter once and never
  overwrites it (ST-0368, ST-0369, ST-0370, ST-0375).
- **Twelve ID prefixes.** `ST`, `BUG`, `SPEC`, `FAGAN`, `SEC`, `RECON`,
  `ATAM`, `IMPL`, `T`, `ADR`, `ARCH`, and `QA` each have their own sequence.
  The new convention `rulebooks/conventions/id-prefixes.md` lists them with
  their ID producers (DEC-25, ST-0383).
- **Every ID producer names its prefix.** Each skill, agent, convention, and
  playbook that creates an indexed artifact names the claim with its literal
  prefix at the step that creates it, for example `next-id FAGAN`. Every step
  that adds a todo entry names `next-id T`. A text test fails when a producer
  drops its prefix (ST-0372, ST-0384, ST-0385).
- **Indexed artifacts may be committed on any branch.** The counter keeps IDs
  unique across branches, so a story or finding no longer has to go to `dev`
  first. Agents may push the claim ref through `next-id`, the one exception to
  the human's ownership of pushes (ST-0373, ST-0374).
- **Fitting step 4 seeds the counter.** VIRGIL runs
  `next-id --plan-seed`, which reads the highest number of each prefix from
  the file names of all local and remote-tracking branches, and runs the seed
  after the human confirms. Every sequence continues without a jump. The
  fitting now has six keys; `counter_seeded` is the sixth, and `init-factory`
  derives it from the counter's remote (ST-0376, ST-0377, ST-0378).
- **A local counter until `origin` exists.** Without `origin`, the project's
  own repository holds the counter, found through the git setting
  `agent-factory.counterRemote`. `next-id --move-to-origin` later moves it to
  the remote and leaves a marker that names the new home. An interrupted move
  resumes on the next run, and a collision with a counter someone else seeded
  stops claims instead of handing out a number twice. VIRGIL offers the move
  at the session start (ST-0379 to ST-0382, DEC-14, DEC-16).

### Changes

- **`RECON` is a finding tag again.** A drift that the reconciliation agent
  records as a finding gets a `RECON` ID; its report row still goes to the
  artifact's owner (DEC-15).
- **A story's `risk_level` is planning risk only.** `backlog-lint` accepts
  `low`, `medium`, and `high`, independent of the test risk classes in
  `docs/testing.yaml`.

### Fixes

- **No token in the clear.** `next-id` and `init-factory` send every line
  they print through one redaction that hides the user info of a remote URL.
  `init-factory` warns when `origin` carries a token in its URL (SEC-0007,
  BR-077, BR-078).
- **A claim keeps the user's ssh command.** `next-id` adds `BatchMode` to the
  ssh command git would run instead of replacing it (IMPL-0004).
- **`dispatch` finds its ledger among several.** It takes the ledger of the
  current branch, `prepare-wave` fails on a wave without stories,
  `verify-story` accepts a short SHA, and `dispatch init` runs without a
  default ledger (BUG-0115, BUG-0116).
- **Tests no longer render the diagrams.** `arch-lint --no-export` skips the
  auto-export of stale diagrams; the default suite uses it, so a test run
  leaves `docs/assets/images` unchanged and starts no container (T-0019).
- **`housekeeping-about` counts six fitting steps** (BUG-0118).

## 1.5.0 — 2026-11-05

This release gives every core artifact one producer and one declared
review (ST-0346 to ST-0367). Run `update-factory` to receive it. The new
gate selection in `premerge-check` takes effect only after the update.

### Features

- **Every output declares its review.** Each output declaration in
  `INDEX.yaml` carries `reviewed_by:` and `edits:`. `index-lint --check`
  fails when a declared reviewer is no agent or does not read the
  artifact. The new core list `rulebooks/core-artifacts.yaml` names the
  core artifacts. A contract test fails on each entry that lacks exactly
  one reviewed producer (ST-0346, ST-0347).
- **The new domain-modeling agent owns the domain structure.** It starts
  once a feature file exists. It writes the glossary, the entity model,
  and the state machines, validation rules, interface contracts, and
  payload schemas the domain needs. The requirements agent keeps the
  scope map, the feature files, and the area specs, and its handoff names
  the domain-modeling agent (ST-0348, ST-0349).
- **Terms wait as candidates.** `reverse-map`, `grilling`,
  `domain-modeling`, and `reconcile-spec` record a term in
  `docs/spec/work/term-candidates.md` when they run outside the
  domain-modeling agent's session. The stakeholder confirms or rejects
  each proposed definition one domain area at a time. Only confirmed
  terms reach `docs/spec/glossary.md` (ST-0350, ST-0351).
- **The new test-strategy agent owns the test practice.** It owns
  `docs/testing.yaml`, the QA strategies, and the test guardrails. It is
  reachable through `intent select` and step 2b of the fitting. Every
  change to `testing.yaml` waits for the stakeholder. A surviving mutant
  that a developer agent cannot resolve becomes a `QA` finding for this
  agent (ST-0357, ST-0358).
- **A finding goes to its owner.** The finding format adds the field
  `owner:` and the tags `ARCH` and `QA`. The orchestrator sends an open
  finding to the agent in `owner:`. A finding without `owner:` goes to the
  producer of the artifact it names. Every open finding in the factory
  repository carries an owner (ST-0352, ST-0366).
- **The architecture agent owns the dependency rules.** It declares
  `docs/spec/dependency-rules.dsl` and writes no `state-machines.md`. A
  contradiction with the state machines becomes an `ARCH` finding for the
  domain-modeling agent. The architecture-review agent checks the rules
  against the component view. Every violation in the report of
  `dependency-check` names the architecture agent as owner (ST-0353 to
  ST-0355).
- **The spec review covers the domain structure.** The spec-review agent
  reports on each structure file that exists and on the glossary. It
  files a finding for every term that waits for confirmation (ST-0356).
- **`premerge-check` picks the gates per story.** It takes the test
  guardrails from the story's `quality-gates` field, then from the
  `gates` section of `docs/testing.yaml`, then runs `crap-score` alone.
  A picked gate that fails blocks the merge. The command warns when the
  house rules still carry the old gate list (ST-0359).
- **The mutation command is a gate.** The new script `mutation-testing`
  runs the project's mutation command from `docs/testing.yaml`. A merge
  is blocked when the command fails, is missing, or exceeds its time
  limit. The developer agent runs the same gates in manual mode before it
  hands a story back (ST-0365).
- **Drift goes to the artifact's owner.** The developer agent writes
  each drift into its story's spec-feedback report and changes no
  specification file. After a merge, the implementation agent dispatches
  the owner of each drift row and then the owner's reviewer. A rejected
  row becomes a `BUG` finding against the code. `dispatch close-wave`
  fails while a drift row is unhandled (ST-0360 to ST-0362).
- **Reconciliation reports rows for owners.** The reconciliation agent
  writes one report per run and changes no other file. Each row names the
  artifact's owner. The `documentation-update` playbook brings each row
  to its owner and then its reviewer, and names every row that still
  waits (ST-0363, ST-0367).
- **Playbooks name the new owners.** Every playbook step that produces a
  moved artifact names its new owner. `run-step` lets the declared inputs
  set the order of the producers. The operator chooses when two agents
  are eligible (ST-0364).
- **`mdformat` keeps footnotes.** The wrapper loads the
  `mdformat-footnote` plugin.

### Changes

- **The finding format drops the `RECON` tag.** Reconciliation drift is a
  row of the reconciliation report, owned by the artifact's owner
  (ST-0352, ST-0363).
- **`draft-proposal` writes the primer before the prose pass.** The
  lector's structural pass then reads the primer next to the Summary.

### Fixes

- **Brownfield onboarding derives the feature file first.** Stage 2 runs
  Derive Feature Spec as Step 3.1, then the vocabulary and the entity
  model as Steps 3.2 and 3.3. The domain-modeling agent needs a feature
  file to start.
- **Onboarding playbooks route `SPEC` findings by owner.** The brownfield
  and greenfield playbooks send each open `SPEC` finding to the agent in
  its `owner:` field.

## 1.4.0 — 2026-11-03

This release reorganises the core artifacts of a project (ST-0318 to
ST-0345). It ships with the merge of `feature/core-artifact-layout` into
dev, commit `e62ac0b077a6d90635b028bdd0e624e1809cde1a`. An update from an
earlier version moves a project's files from the old layout into the new
one.

### Features

- **One specification layout.** The single-file core artifacts stay at the
  top of `docs/spec/`: the scope map, the glossary, and the Structurizr
  model `architecture.dsl`. Feature files move to `docs/spec/features/`.
  Working output such as gap reports, QA strategies, `prd.md`, and the
  todo lists moves to `docs/spec/work/`. Every agent, skill, playbook,
  and gate reads and writes the new paths (ST-0325, ST-0326, ST-0338 to
  ST-0342).
- **The new script `migrate-spec-layout` moves a project.** It moves each
  file to its new path, and git records each tracked file as a rename.
  It rewrites every Markdown link to a moved file, so `link-check` passes
  afterwards. It lists every old path outside a Markdown link with its
  file and line and leaves those files unchanged. It updates the factory
  hook block to the new hook template. `--dry-run` prints the planned
  moves and link rewrites without changing a file (ST-0318, ST-0320 to
  ST-0322).
- **The migration removes use-case files.** It removes
  `actor-goal-list.md` and every `use_cases/` folder under `docs/` with
  `git rm`, the archive included. Agents find a story's behaviour in the
  scope map and the feature files. `spec-lint` checks business rules
  without use-case files (ST-0319, ST-0327, ST-0340).
- **One glossary.** `docs/spec/glossary.md` holds every term in tables with
  the columns Term, Definition, and Avoid. The migration turns the tables
  of chapter 12 into glossary sections and leaves a link line in
  `docs/arc42/12_glossary.md`. It moves the `## Language` terms of every
  `CONTEXT.md` into the glossary and lists each term that appears twice.
  `domain-modeling` and `reverse-map` write terms there, and the review
  and interview skills look them up there. `publish-docs` prints the
  glossary as chapter 12 without a change to the manifest (ST-0323,
  ST-0324, ST-0334, ST-0336, ST-0337).
- **Routing files fold into the agent context.** The new mode
  `capture-context --fold-context-map` writes one domain concern per
  context into `docs/agent-context.md` and points every link at that file.
  Agents then route through that file instead of `docs/CONTEXT.md` and
  `docs/arc42/CONTEXT-MAP.md`. The developer deletes the old files. A
  rescan with `capture-context --update --scan` keeps every folded concern
  (ST-0328, ST-0329, ST-0344).
- **The update migrates, and a first install does not.** An approved
  update from a version before 1.4.0 runs the migration without a further
  question and records the new version in `.agent-factory/install.json`.
  A failed migration rolls back the project files, the hook block, the
  factory tree, and the version. A first install on a project in the old
  layout moves no file, lists the old paths, and names
  `migrate-spec-layout` (ST-0330 to ST-0333).
- **Feature work checks four anchor files.** `feature-addition` and the
  Stage 1 exit of `brownfield-onboarding` check `docs/spec/architecture.dsl`,
  `docs/spec/scope-map.md`, `docs/spec/glossary.md`, and
  `docs/agent-context.md`. When a file is missing, the playbook names it
  (ST-0335).
- **The factory's own repository uses the new layout.** A test in the
  default suite fails when an old path returns to `packages/factory/`
  (ST-0343, ST-0345).

### Fixes

- **A migration never replaces a file.** Two old QA strategy files can map
  to one new path. The second one moves to
  `docs/spec/work/<name>-area-qa-strategy.md`, and the script lists the
  pair. A taken destination stops the script with exit 2 before the first
  change (IMPL-0001).
- **The migration reads old `CONTEXT.md` forms.** It converts `###`
  subheadings and bullet terms under `## Language`, which the old format
  rules allowed. Such a file no longer stops the migration (IMPL-0002).

## 1.3.3 — 2026-10-27

### Fixes

- **Briefs stay in the main checkout.** On every CLI, the dispatch
  contract puts briefs and scratch files in the main checkout. A brief
  goes to `.current-work/<branch>/briefs/<task>.md`, and a scratch file to
  `.current-work/<branch>/scratch/<agent-or-story>/`. The prompt names the
  brief by absolute path. Briefs no longer sit under `/tmp`, which the
  system can empty.
- **Briefs name factory files in the main checkout.** A linked worktree
  holds no `.agent-factory/`. So a brief names each factory input by
  absolute path under `<main checkout>/.agent-factory/factory/`
  (BUG-0092).
- **Pi worktrees follow the rulebook.** Pi's `dispatch-wave` cuts
  worktrees under `.current-work/<target>/`, and its git guard accepts any
  path under `.current-work/`, as `rules.md` and the Claude guard do
  (BUG-0102).
- **One main-checkout helper.** `scope-lint`, `concern-lint`, and
  `link-check` share the new module `_main_checkout.py` instead of three
  copies (BUG-0103).

## 1.3.2 — 2026-10-27

### Fixes

- **The hook refresh keeps a project's keys.** `update-factory` replaces
  only the keys the factory's template uses on its hooks: `id`, `name`,
  `entry`, `language`, `pass_filenames`, `files`, `exclude`, `types`, and
  `stages`. It keeps every other key a project set on a factory hook,
  such as `args:`. The 1.3.1 refresh dropped such keys. If commits that
  touch `backlog/` fail since 1.3.1, add the `args:` line that passes
  `--exclude` to `backlog-lint` once more. Later refreshes keep it
  (BUG-0112).
- **Factory hook lines fit in 80 columns.** Each hook `entry` is a folded
  YAML scalar broken at spaces, so the command stays the same. Three hook
  names are shorter, and two long `files:` regexes sit on their own line.
  A fresh or refreshed `.pre-commit-config.yaml` passes yamllint with its
  default rules. After the refresh, you can remove a per-file yamllint
  ignore for that file (BUG-0113).

## 1.3.1 — 2026-10-27

### Fixes

- **The test hook runs in parallel.** The `run-tests` hook runs pytest
  with `-n auto` and skips the tests marked `container`. The 15
  `publish-docs` tests that render a PDF in a container run on demand
  with `pre-commit run run-container-tests --all-files --hook-stage manual`.
  `docs/testing.yaml` uses the same command, so dispatch verifies stories
  the same way.
- **Test dependencies are declared.** `pyproject.toml` lists pytest,
  pytest-xdist, PyYAML, Radon, and tiktoken in uv's `dev` group, which
  `uv run` installs. The hook no longer depends on the pytest on the
  developer's PATH.

## 1.3.0 — 2026-10-27

### Features

- **Factory hooks tell a colleague from a broken install.** `init-factory`
  sets `agent-factory.installed` in the clone's local git config, and
  `remove-factory` unsets it. When `.agent-factory/` is missing, a hook
  in a clone without the key passes in silence. So a colleague without
  the factory commits as before. A hook in a clone with the key fails and
  names `update-factory` and `SKIP`. Existing installs get the key on
  their next `update-factory` (BUG-0111).

- **update-factory refreshes the project's hooks.** After the update,
  `update-factory` compares the project's `agent_factory_hook-*` block
  with the new template. When they differ, it shows the diff and writes
  only on an explicit yes. `merge-precommit-config --update` replaces the
  block where it stands and keeps the comments around it (BUG-0110).

- **backlog-lint can skip files.** The new option `--exclude GLOB`
  (repeatable) skips files in `backlog/` whose name matches the glob. So
  a file such as `ST-0003B-details.md` is not linted as a story. The
  pre-commit hook passes `args:` on to `backlog-lint` (`"$@"`).
  `update-factory` offers the new hook entry. Without `--exclude`, nothing
  changes (GB-5494).

- **Brownfield onboarding builds the scope map from code.** Stage 1 of
  the brownfield playbook runs the archive step, `reverse-map`, and then
  the Structurizr model. `reverse-map` has an unattended mode that writes
  a scope map with `status: draft`. The Stage 1 exit fails on a draft map
  (`SCOPE001`) and on a `spec-lint` crash. `derive-feature` has a
  brownfield entry from the scope map and stops on a draft. The
  requirements agent takes the brownfield branch only when it receives
  the scope map as input (ST-0313 to ST-0317, BUG-0093 to BUG-0096).

- **Architecture docs as one PDF.** The new skill `publish-docs` builds
  the arc42 documentation into `docs/dist/<project>-architecture.pdf`.
  The manifest `docs/publish-docs.yaml` lists the documents. The script
  validates and exports the Structurizr model, assembles a Quarkdown
  build, and renders it in a container with Quarkdown 2.6.4 and Chromium.
  When a render check fails, the script removes the PDF. The layout uses
  10 pt type and dotted table rules. Each appendix document, such as an
  ADR, starts on a new page (ST-0309 to ST-0312).

- **A primer for every proposal.** The new skill `write-primer` writes a
  plain-language introduction of 400 to 500 words for a reader who knows
  nothing about the project. `draft-proposal` runs it in a fresh subagent
  before the gate, and the gate checks that the primer still matches.

- **Proposals separate design from record.** The proposal states the
  design in the present tense. An appendix holds the Decisions, Review
  findings, and Review passes tables. A review finding moves from open to
  fixed to resolved, so an unchecked fix stays visible.

- **Subagents start fresh by default.** Every CLI starts a subagent with a
  brief file. A Claude Code fork is used only when the child needs the
  conversation itself.

- **Working discipline.** The new rulebook `working-discipline.md` and six
  rules in `rules.md` set how agents check premises, handle errors, and
  stop a failing approach. An agent marks a claim about an external tool
  as unchecked unless it checked the claim in the session.

- **YAML files begin with `---`.** `init-factory` writes `testing.yaml` and
  a new `.pre-commit-config.yaml` with the document marker. The new
  convention `yaml-format.md` states the rule. An excerpt meant for
  existing front matter carries `<!-- yaml-excerpt -->` and no marker
  (ST-0308).

### Fixes

- **Brownfield checks hold.** `scope-lint` reads workstream IDs from the
  main checkout when it runs in a linked worktree. A `.dsl` file declares
  its scope with `# scope:` on line 1, and `// scope:` still passes.
  Agent definitions accept an `any_of` form for required inputs, and
  `index-lint` rejects a malformed one. The architecture agent does not
  archive the new scope map (BUG-0093 to BUG-0096).
- **urllib3 2.8.0.** The usage runtime requirements pin urllib3 2.8.0,
  which resolves one vulnerability finding.
- **Bug-hunt fix run.** The bug-hunt fix run (ST-0295 to ST-0308) resolves
  31 findings. BUG-0076 and BUG-0079 are partly fixed and stay open.
  - **Gates fail closed.** A gate whose input directory is missing exits 2
    instead of passing. Gates in a story worktree find the installed
    factory (BUG-0039 to BUG-0041, BUG-0054).
  - **Lint scripts read their input correctly.** `arch-lint`, `backlog-lint`,
    `concern-lint`, `conjecture-lint`, `context-lint`, `dependency-check`,
    `handoff-lint`, `index-lint`, `link-check`, `mermaid-lint`,
    `module-graph-check`, `schema-validate`, `spec-lint`,
    `statemachine-lint`, and `test-design-verify` each fix a parsing or
    exit-code defect (BUG-0049 to BUG-0063, BUG-0071, BUG-0090, BUG-0091).
  - **crap-score finds the right coverage.** It resolves coverage keys
    against one base where every key exists. It reads PEP 263 coding lines
    and fails on a file it cannot parse (BUG-0072).
  - **commit-safe commits only staged work.** The second pass re-stages only
    the paths staged before the first pass. Unstaged lines of a staged file
    stay out of the commit (BUG-0080).
  - **dispatch runs a wave end to end.** `merge-story` is safe against
    interrupted merges and scopes by `touches` when `outputs` is absent. The
    new `refresh-story` command refreshes a story branch before merge
    (BUG-0036 to BUG-0038, BUG-0082 to BUG-0085, BUG-0087,
    BUG-0089).
  - **Install, update, and removal keep project files.** `init-factory` and
    `remove-factory` keep a `.claude/hooks` or `.codex` directory that
    existed before the install. `update-factory` keeps the install record
    and restores only factory-owned wiring on rollback. Claude include paths
    are relative to each instruction file. A stale removal owner file is
    taken over atomically. `merge-precommit-config` detects an earlier merge
    by any factory hook id (BUG-0048, BUG-0074 to BUG-0079, BUG-0081).
  - **build-release builds from HEAD.** It reads the version from HEAD,
    keeps earlier assets when a rebuild fails, and warns about uncommitted
    changes in `packages/factory/` (BUG-0073).
  - **Usage capture works in installed projects.** Claude Code usage counts
    once per message id. A cut-off character in a transcript skips one line.
    Usage capture reports itself as broken, idle, or healthy (BUG-0033 to
    BUG-0035, BUG-0064, BUG-0066, BUG-0068 to BUG-0070).
  - **The charter gates are retired.** Epic 0 and the gates that depended on
    the charter are removed. The new planning gate passes on a fresh project
    (BUG-0047).
  - **Instructions name commands that exist.** Update instructions point to
    `update-factory`, which the developer runs. The guide states that the
    step guard does not enforce step manifests yet (BUG-0042 to BUG-0046).

## 1.2.0-rc — 2026-10-01

### Features

- **One voice for every text.** The new rulebook `factory-voice.md`
  defines how the factory writes. It covers chat replies, status reports,
  handoffs, commit messages, findings, stories, and specifications. It
  replaces `writing-quality-gates.md`, which is removed. The voice ends
  with four gates and a final pass that removes buzzwords. Terms of the
  trade, such as SQL or API, need no definition. Project terms still do.
- **Every agent and skill loads the voice.** All 17 agents and 49 skills
  start with one fixed sentence that loads `factory-voice.md`. The new
  `voice-anchor-lint` script checks that sentence in pre-commit and as
  gate 13 in `validate`. It runs only in the factory source repository.
  The script lists seven skills whose output is mechanical or exempt.
- **Review findings explained for newcomers.** The new skill
  `explain-review-finding` explains a finding, bug report, or failing
  test. It checks the finding against the code first. It then states the
  consequence, shows a short chain of cause and effect, and names the
  smallest fix. It never edits code. `code-review-agent` offers it while
  the user decides which findings to file.
- **Defects state the consequence first.** `fagan-review` writes each
  Defect in a fixed order: the consequence and who receives it, the first
  layer where the problem starts, and whether the behavior looks
  intended, wrong, or undocumented.

### Fixes

- **Voice declaration cleaned up.** A stray `\<` at the start of
  `factory-voice.md` is removed. Two lines in `proposal-review-agent` and
  `newcomer-tour` that asked for a different tone now match the voice.
- **VERSION without prefix.** `VERSION` does not start with `v`, so
  `build-release` accepts it.

## 1.1.1 — 2026-09-29

### Fixes

- **crap-score lists each method once.** Radon's `cc_visit` returns every
  class method as its own block, and `flatten_blocks()` added each one a
  second time. Class blocks are now dropped, so each method appears once
  in the report. The scores were correct before the fix.

## 1.1.0 — 2026-09-29

### Features

- **Structurizr default theme vendored locally.** The `default` theme
  from `structurizr/structurizr` sits in
  `packages/factory/themes/structurizr/default/` and ships with every
  factory install. `architecture.dsl` uses a local relative path
  (`theme themes/default/theme.json`) instead of `theme default`. The
  remote theme resolved to `static.structurizr.com`, a host decommissioned
  on 30 September 2026. `scaffold-arc42` copies the theme into new
  projects. Other themes (AWS, Azure, GCP) can be added the same way from
  the upstream GitHub repository.

### Fixes

- **A fresh init-factory install starts at 0/5, unfitted.** A fresh
  install does not derive fitting keys from leftover artifacts of an
  earlier installation.

## 1.1.0-rc — 2026-09-28

This release implements the fifteen stories of the value-first onboarding
journey (ST-0280 through ST-0294). It also adds GitHub Actions CI for
release builds and the preserve-dirs guard.

### Features

- **Value-first onboarding.** All fifteen stories are implemented:
  - The build-release script packages the factory into a versioned tarball
    with SHA-256 checksums under `releases/<version>/` (ST-0280).
  - The standalone `install-agent-factory` script installs the factory from
    a local source directory into any target project. It checks
    prerequisites, detects the CLIs, shows a preview that needs consent,
    and prints an installation receipt with next steps (ST-0281).
  - `install-agent-factory --source <url>` downloads a release tarball,
    checks its SHA-256 digest against `SHA256SUMS`, and installs it
    (ST-0282).
  - The installer detects missing prerequisites (uv, git) and says how to
    fix them. It loops until the prerequisites are met or the user aborts
    (ST-0283).
  - `update-factory --check` runs as a dry run. It reports the installed
    and the candidate version, the changed files, and the CLI list, and it
    modifies nothing (ST-0284).
  - `update-factory` verifies staged updates and rolls back automatically
    when an update fails. It backs up user-changed files to
    `.agent-factory/user-changes/` (ST-0285).
  - When the update source type changes, from local to remote or back,
    `update-factory` asks for explicit consent before it continues
    (ST-0286).
  - Virgil's first greenfield session leads with a key-value project
    insight (Stack, Test entry, Safety signal, Recommended action) and
    then presents the session menu (ST-0287).
  - After the project insight, context capture is offered as a recommended
    action and does not run by itself. The explanation says what data it
    collects and why (ST-0288).
  - Before the user decides on the hook configuration, a live gate
    demonstration shows what the gates protect and how they fire
    (ST-0289).
  - Hook configuration groups hooks by the outcome they protect, not by
    hook name. Target projects do not see triggers that apply only to the
    factory source (ST-0290).
  - The isolated first-task sandbox starts only in an empty repository. A
    repository with commits gets the normal session behavior (ST-0291).
  - `init-factory` creates a plain sandbox when the target repository has
    no HEAD, so `git log` and `git diff` do not fail (ST-0292).
  - An automated test harness runs the journey from greenfield to insight
    to menu to first task (ST-0293).
  - A template guides moderated usability tests of the onboarding flow,
    with comprehension checkpoints (ST-0294).
- **Preserve-dirs guard.** Before a reinstall, `init-factory` backs up
  non-empty `usage/` and `user-changes/` directories. After the install,
  it compares their subdirectory structure with the new install. It
  offers a restore in an interactive run and restores automatically in a
  non-interactive run. It prints the backup path when the structure does
  not match.
- **GitHub Actions CI.** The `build-release.yml` workflow runs on a tag
  push (`v*`) and on a push to the dev branch. It creates GitHub releases
  with `install-agent-factory`, `agent-factory.tar.gz`, and `SHA256SUMS`.

### Fixes

- **build-release branch constraint.** The constraint allows `-rc` builds
  on branches other than main and dev, such as feature branches.
- **Greenfield routing in orientation files.** The `AGENTS.*.md`
  orientation files route `fitting.status = "greenfield"` to the
  first-session insight procedure instead of the session menu.
- **update-factory TypeError.** `update-factory` does not crash when
  `manifest.get("cli")` returns a list instead of a string.
- **Install receipt text.** The "Next" section of the installation receipt
  is clearer.
- **.gitignore trailing-slash semantics.** The `.agent-factory/` pattern
  with a trailing slash matches directories only. Symlinks created by
  ST-0294 no longer slip through.
- **Bare .github in .gitignore.** The bare `.github` line is removed. It
  kept all `.github/` content from being tracked.

### Documentation

- **Usage data recovery proposal.** The draft proposal at
  `docs/proposals/usage-data-recovery.md` documents the raw transcript
  inventory across four CLIs (518 sessions), the capture pipeline, two
  recovery options, a metadata quality matrix, and prevention.

### Tests

- **Preserve-dirs guard tests.** Nine tests in `test_init_factory.py`
  cover the guard. Five test `backup_preserved_dirs`: skip conditions,
  non-empty backup, and symlink handling. Four test
  `offer_restore_preserved_dirs`: structure match, mismatch, missing
  directory, and non-interactive restore.

## 1.0.0 — 2026-09-21

This release implements activity graph orchestration (ST-0262 through
ST-0278) and local usage processing and analysis (ST-0240 through ST-0251).
The activity graph supersedes the cycle-based orchestration proposal, and a
reconciliation after implementation resolves 52 findings.

### Features

- **Activity graph orchestration.** All seventeen stories are
  implemented:
  - Typed precondition objects (`inputs.required`, `inputs.context`,
    `outputs.declarations`) replace the flat inputs/outputs lists in all
    17 agent definitions. `index-lint` is rewritten for the new format
    (ST-0262).
  - A precondition evaluator decides eligibility. It checks typed
    conditions against project state (ST-0263).
  - The intent select command shows every agent with its precondition
    evidence, so the developer can select one in the Project Work lane
    (ST-0264).
  - Behavioral verification tests check the activity-graph model
    (ST-0265).
  - The fence runner validates output against activity-graph assertions
    and stores the evidence (ST-0266).
  - The intent assess subcommand validates artifacts (ST-0267).
  - The session menu changes from 5 options (A–E) to 4 lanes (H, K, P, O)
    (ST-0268).
  - Workstream state v2 adds modules for the workstream lifecycle and
    binds a session to a workstream (ST-0269).
  - The Project Work lane of the session menu creates and continues
    workstreams (ST-0270).
  - The housekeeping about section shows the factory state and offers
    re-fit and update actions (ST-0271).
  - `capture-context` gains `--update --scan`, which refreshes an existing
    `docs/agent-context.md` (ST-0272).
  - The scope-lint script validates the scope of governed artifacts
    deterministically (ST-0273).
  - Governed artifacts declare their scope in frontmatter, and lint and
    dispatch filter by it (ST-0274).
  - `factory/` moves under `.agent-factory/factory/`, and every internal
    reference follows (ST-0275).
  - `packages/orchestrator` is retired. The tests that are still needed
    move to `packages/factory` (ST-0276).
  - The cycle-based orchestration proposal is superseded, and
    characterization tests are added (ST-0277).
  - Structured JSONL stays alongside the text rendering (ST-0278).
- **Local usage processing and analysis.** All twelve stories are
  implemented:
  - The canonical usage-record schema is defined, and the `packages/usage`
    package is scaffolded (ST-0240).
  - The usage-contract-check gate checks the schema and the cross-field
    rules of the usage-record contract (ST-0241).
  - The usage-query CLI queries usage data and captures a snapshot of its
    input (ST-0242).
  - An operational preflight checks run lineage with six ancestry failure
    codes before a query runs (ST-0243).
  - The capture_health view, a diagnostic view with stable-view refusal,
    detects capture health issues across sessions (ST-0244).
  - Four-CLI conservation rules keep usage accounting consistent across
    all four CLI entry points, with the canonical_session_usage view
    (ST-0245).
  - Four more views complete the six-view query surface (ST-0246).
  - Result format adapters return table, JSON, relation, or Arrow output
    (ST-0247).
  - The atomic Parquet export tracks provenance and has a dependency gate
    (ST-0248).
  - `init-factory` registers usage-analysis as a factory component with
    install and update lifecycle hooks (ST-0249).
  - A capture-independence test checks the dependency boundary: the usage
    package does not depend on capture internals (ST-0250).
  - An interactive DuckDB UI explorer has a persist mode, an HTTP server,
    and a smoke gate (ST-0251).
- **Usage explorer live-watch mode.** `usage-explore` gains a
  file-watching mode. It refreshes the DuckDB view when a JSONL source
  file changes.
- **Agent and skill inventory cleanup.** Shared conventions move into
  reusable reference files. Overlapping agents and skills are merged.
  References to the flipped-default principle trim the overlap with
  native knowledge. A guideline defines how to write a skill. Deprecated
  skills are removed, and their references are updated.
- **EPIC slicing gate strengthened.** Grilling and the concreteness pass
  are enforced more strictly before stories enter the backlog.
- **Research directory layout convention.** The new convention
  `rulebooks/conventions/research-directory-layout.md` sets one output
  structure for the survey and falsification playbooks.
- **Research playbooks updated.** The `research-survey` and
  `research-topic` playbooks reference the directory layout and handle
  source records better.
- **DuckDB dependency bumped to >=1.3.0.** The usage explorer needs this
  version for the UI extension.

### Fixes

- **Broken links after layout migration.** All `factory/` references in
  rulebooks, templates, poc, and findings point to
  `.agent-factory/factory/`.
- **arch-lint SVG diagrams.** The diagrams are regenerated after the link
  migration.
- **arch-lint conditional export.** arch-lint exports only when the DSL
  is newer than the youngest SVG, so it skips needless regeneration.
- **File-modifying hooks restricted to commit stage.** Hooks that rewrite
  files fire only at the commit stage, not on other tool calls.
- **Invalid YAML frontmatter.** Malformed frontmatter in governed
  artifacts is fixed.
- **ROOT_COUNT per connected component.** The conservation check
  validates ROOT_COUNT within each connected component instead of
  globally per CLI.
- **source_root detection.** The detection walks up to the monorepo root
  instead of stopping at the nearest package.
- **File path resolution.** Paths resolve to absolute paths before uv
  changes the working directory.
- **Explorer HTTP server.** The server sets `allow_reuse_address`, so a
  restart does not fail with "address already in use".
- **Usage package installation.** The full runnable package installs with
  convenience wrapper scripts.
- **Scope check fallback.** The check falls back to `touches` when a
  story has no `outputs` frontmatter.
- **Pi-specific errors.** The AGENTS.md orientation for Pi is simpler.
  The TypeScript extension imports in `dispatch-wave.ts`, `run-agent.ts`,
  `pi-usage.ts`, and `step-guard.ts` are corrected. The init-factory CLI
  detection is more reliable.
- **Stale agent-context entries.** The obsolete
  `Factory source_root and packaging` section is removed from
  `docs/agent-context.md`.

### Refactoring

- **Usage submodule rename.** Module names drop the `canonical_` prefix.
  CRAP scores in the usage submodules are lower, and unit tests are
  added.
- **Root convenience scripts removed.** The `usage-query` and
  `usage-explore` wrappers are removed from the project root.
- **FSM phase harness removed.** The `phase` script (631 lines), the
  `transition-lint` script (393 lines), the `cycle` script (406 lines),
  and the FSM definition files (`*.fsm.yml`) are deleted. The activity
  graph replaced the cycle engine, so this code was dead. About 30 live
  docs now describe the precondition-based eligibility model. Cycle-based
  spec files are archived under `docs/~archive/`.
- **`run-playbook` script removed.** The activity graph replaced
  playbook-based flow control, so the script had no callers.
- **Cycle-engine diagrams replaced.** `CycleEngineComponents` is renamed
  to `AgentSelection`, and `CycleTransition` to
  `EligibilityEngineComponents`. A new `AgentDependencyGraph` diagram is
  added.

### Documentation

- **Activity graph orchestration — full lifecycle.** The proposal is
  accepted, the specification derived, the architecture extended, and
  the backlog planned (7 EPICs, 17 stories). All stories are implemented
  and merged.
- **Cycle-based orchestration — superseded.** The proposal was accepted,
  its specification derived, and its architecture added. The ATAM
  findings ATAM-0003 through ATAM-0009 and four spec-review findings
  (SPEC-0023 through SPEC-0026) are resolved. The stories are rejected,
  and the activity graph supersedes the proposal.
- **OpenCode CLI integration proposal.** The full proposal is at
  `docs/proposals/opencode-cli-integration.md` (status: open). Its
  research survey (12 sources) moves to
  `docs/research/opencode-cli-integration/`.
- **Agent Zero research survey.** The survey at
  `docs/research/agent-zero/` has 7 source records and a report. The
  report evaluates Agent Zero's architecture, extension points, and
  possible integration with the factory.
- **Architecture reconciled.** Chapters 5 (building block view),
  6 (runtime view), 7 (deployment view), 8 (crosscutting concepts),
  and 9 (architecture decisions) describe the activity graph in place of
  the cycle engine. The Structurizr DSL workspace is updated. The
  glossary and the context map are corrected.
- **Factory guide rewritten.** The guide covers the `.agent-factory/`
  paths and the HKPO session menu layout.
- **Newcomer onboarding specification updated.** Four scenarios are
  rewritten for the HKPO session menu.
- **Scope map reconciled.** The scope map is updated after the layout
  migration and the activity-graph implementation.
- **PRD updated.** Path references are corrected for the
  `.agent-factory/` layout.
- **Hermes Host Adapter proposal.** A draft proposal is at
  `docs/proposals/hermes-host-adapter.md`.
- **Concept-Stage Knowledge Inventory proposal.** A draft proposal is at
  `docs/proposals/concept-stage-knowledge-inventory.md`.
- **Browser exploration guide.** The guide documents the DuckDB UI and
  Web-UI exploration paths.

### Tests

- **Activity-graph behavioral tests.** Test suites check the behavior of
  the activity-graph model: precondition evaluation, eligibility, fence
  runner, intent commands, housekeeping, and recommendations.
- **Capture-independence integration test.** The test checks that the
  usage package does not depend on capture internals.
- **Scope-lint tests.** The tests validate scope declarations in governed
  artifacts.
- **Workstream and session-binding tests.** The tests cover the lifecycle
  and binding modules of workstream state v2.

## 0.12.0 — 2026-09-14

This release runs the full pass from specification to backlog for local
usage processing and analysis. It adds the cycle-based orchestration
proposal. It adds a fourth writing quality gate ("No Pretense") and a
stronger skill preamble in all 37 skills that produce prose. arch-lint
handles extended building-block views and filters diagram key files.

### Features

- **No Pretense writing gate.** `writing-quality-gates.md` gains a fourth
  gate. Every verb in a Goal names something observable from outside, and
  internal mechanism belongs in Scope. Constraints go in the Constraints
  section and are not presented as accomplishments. Ordinary operations
  get plain verbs, and simple operations are not dramatized. The gate has
  eight concrete checks.
- **Skill preamble hardened.** All 37 prose-producing skills change their
  preamble from "Apply the writing quality gates" to "Read
  writing-quality-gates.md now and hold every rule as a writing
  constraint. No prose reaches terminal output or a file until it passes
  all four gates."

### Fixes

- **arch-lint component scan range.** `ch5_core_components` scans all
  §5.x sections up to "Referenced from" instead of stopping at §5.5. So
  the consistency check includes components defined in §5.5 and later.
- **arch-lint SVG key-file filtering.** Image enumeration excludes
  `*-key.svg` legend files and considers only SVGs that have a matching
  key file. Standalone legend images no longer cause false positives.
- **Stale cross-reference in SPEC-0015.** A dead link to a superseded
  agent-context feature is removed.

### Documentation

- **Local Usage Processing and Analysis — specification complete.** The
  full requirements pass produces a consolidated Gherkin feature file (14
  rules, 48 scenarios), supplementary specs (entity model, interface
  contracts, state machines, validation rules), a QA strategy, and a gaps
  report. Four specification review rounds filed and resolved eight
  findings (SPEC-0015 through SPEC-0022).
- **Local Usage Processing and Analysis — architecture complete.** The
  arc42 chapters 5 (building block view with §5.5 interfaces), 6
  (runtime view), 7 (deployment view), 8 (crosscutting concepts), and
  9 (architecture decisions) are extended. ADR-0015 is accepted: query
  authoritative JSONL with ephemeral DuckDB views. The Structurizr DSL
  workspace gains usage-analysis containers, components, and four new
  views. Six new SVG diagrams are exported.
- **Local Usage Processing and Analysis — backlog complete.** Twelve
  stories (ST-0240 through ST-0251) across three EPICs carry testability
  probes, MoSCoW priorities, and a dependency order. ST-0240 and ST-0241
  are grilled and made concrete.
- **Cycle-based orchestration proposal.** The new proposal at
  `docs/proposals/cycle-based-orchestration.md` (status: open) has passed
  its first adversarial review.
- **Scope map updated.** `docs/spec/scope-map.md` gains scope entries for
  local usage processing and analysis.
- **Epics file renamed.** `backlog/epics.md` is renamed to
  `backlog/epics-test-design-redistribution.md`, so its name states its
  feature. The new `backlog/epics-local-usage-analysis.md` is added.

## 0.11.0 — 2026-09-12

This release hardens the playbooks, makes backlog stories concrete, and
resolves five manifest defects. The code-review agent and review-mode
dispatch add a human inspection loop to the implementation phase. Two new
backlog skills keep stories short and concrete before they enter the
backlog. Five bug reports showed manifest gaps that blocked deterministic
phase handoffs. All five are resolved, with regression tests.

### Features

- **Code review agent.** The new `code-review-agent` (phase 4, tier
  strong) runs a bounded Fagan inspection on the implementation diff
  before the reconciliation run. It reviews changed files only, with no
  security review and no bug hunt. It files findings as `IMPL-*`. Every
  finding passes three quality gates before filing: international-English
  clarity, a fix direction for a junior developer, and brevity for a
  senior engineer. The `feature-addition` and `greenfield-development`
  playbooks gain Step 4.2 (code review) and Decision Point 4.3 (IMPL-\*
  check) between implementation and reconciliation. The FSM gains the
  states `PHASE_4_CODE_REVIEW` and `PHASE_4_IMPL_FIX`. The implementation
  agent hands off to code-review-agent instead of reconciliation-agent.
- **Ledger-backed implementation review mode.** A serial workflow runs on
  one `feature/<name>` branch in the primary checkout. A human inspects,
  stages, and commits each story with the full local development
  environment. The new commands `dispatch init-review`, `review-dispatch`,
  `review-accept`, and `review-close` enforce clean boundaries, exact
  commit ancestry, story IDs, atomic `status: done`, declared output
  scope, passing tests, and terminal closure. Direct creation of
  standalone branches stays blocked, and autonomous dispatch commands
  reject review-mode ledgers.
- **Split story IDs.** The story template and `backlog-lint` accept
  split-story IDs (`ST-NNNNA`, `ST-NNNNB`) for stories split after their
  first numbering.
- **Risk-class extraction in detect-test-regime.** The
  `detect-test-regime` skill extracts `risk_classes` from the project's
  testing configuration. Test design during implementation can then take
  risk into account.
- **Concreteness and slicing skills.** The create-backlog sequence gains
  two backlog skills. `create-backlog-make-concrete` runs every story
  through a concreteness checklist before acceptance.
  `create-backlog-slice-story` splits a story that needs more than one
  implementation pass into slices that ship independently. The grilling
  skill gains more concreteness probes.
- **Short, actionable stories.** `create-backlog-stories` and the parent
  `create-backlog` skill require shorter story bodies in concrete
  behavioral language. The story template gives tighter guidance per
  section.
- **Draft-proposal skill enhancement.** The `draft-proposal` skill
  structures proposals better, scaffolds estimates, and routes
  cross-cutting concerns through the agent context.
- **Review-workspace-check script.** The new `review-workspace-check`
  script validates the workspace state before a review-mode operation
  begins.
- **Reconciliation agent update.** The reconciliation agent definition is
  shorter, so the handoff from code-review-agent is clearer.

### Fixes

- **Proposal-to-requirements handoff boundary (BUG-0024).** The feature
  workflow can enter Requirements after a proposal is accepted.
  `handoff-format.md` and `handoff-lint` add the missing boundary
  `proposal intake -> requirements` to the boundary registry. Regression
  tests cover valid and invalid boundaries.
- **Backlog-lint test contract (BUG-0025).** The `valid_risk_levels`
  argument from 0.10.0 broke 23 tests in `test_backlog_lint.py` that used
  the old `check_story` signature. All direct unit-test callers pass the
  default set of risk levels.
- **Story quality-gate enum (BUG-0026).** `ST-0217` and `ST-0221` declare
  the canonical `mutation-testing` instead of `mutation-analysis`, so
  they pass `BL-ENUM` validation.
- **Specification-review manifest (BUG-0027).** The `feature-addition`
  spec-review step admits `docs/CONTEXT.md` as input and
  `docs/reviews/spec-review-*.md` as output. So the `inspect-spec`
  workflow can read terminology context and write its review report. A
  manifest-contract test is added.
- **Requirements remediation manifest (BUG-0028).** The
  `feature-addition` update-specification step admits
  `docs/findings/SPEC-*.md` as input and `docs/proposals/**/*.md` as
  output. So a Requirements Agent can read specification defects and
  correct an accepted proposal after a failed review. The
  manifest-contract test covers both paths.

### Documentation

- **Deterministic Factory Engine proposal.** The draft proposal at
  `docs/proposals/deterministic-factory-engine.md` moves flow-control
  logic into an engine package of its own. A consultative review produced
  four grilling findings (PROP-0021 through PROP-0024).
- **Local Usage Processing and Analysis proposal accepted.**
  `docs/proposals/usage-processing-and-storage.md` grows from draft to
  accepted, with the full design, entity model, query interface, and
  dependency contracts. The specification review filed five findings
  (SPEC-0015 through SPEC-0019).
- **Factory guide expanded.** The factory guide documents review-mode
  dispatch.

### Tests

- **Dispatch review-mode tests.** A 365-line test suite
  (`test_dispatch_review_mode.py`) covers the review-mode dispatch
  workflow.
- **Feature-addition contract tests.** The new
  `test_feature_addition_contract.py` checks that the playbook step
  manifests admit every required input and output path.
- **Handoff-lint tests.** The new `test_handoff_lint.py` covers boundary
  regressions.
- **Review-workspace-check tests.** The new
  `test_review_workspace_check.py` tests the workspace check.
- **Backlog-lint risk-level alignment.** Existing tests follow the
  `valid_risk_levels` contract.

## 0.10.0 — 2026-09-09

This release brings the agent-ready story format and moves test design to
a different layer. A developer-agent implements a story from the planning
agent in a single pass, with no rewrite step afterwards. Test design moves
from planning time to implementation time. The developer-agent owns test
authoring through a two-pass TDD model.

### Features

- **13-section story template.** 13 sections replace the 7-section
  body (Demo, Acceptance Criteria, Scope, Terminology, Notes for the
  Implementer): Goal, Domain Rule, Demo Scenario, Affected Paths,
  Inputs, Outputs, Required Behavior (conditional), Constraints,
  Suggested Agent Plan, Acceptance Criteria, Verification, Out of Scope,
  Agent Stop Conditions. Each section is defined so a developer-agent can
  implement the story without rereading the planning context.
- **`risk_level` frontmatter field.** The story template and backlog-lint
  accept the optional enum `low | medium | high`. backlog-lint validates
  it with the error code `BL-ENUM`. Three tests are added.
- **`touches` hygiene rule.** The story template documents the rule under
  Affected Paths. List only the most specific existing directories, and
  never a parent together with its child. List no speculative path for a
  directory that does not exist yet. Every entry resolves to an existing
  directory or to one that a story in `deps` creates.
- **Composition rules updated.** Rule 1 becomes "Goal First, then Demo":
  write the Goal statement before the Demo Scenario. The new Rule 4,
  "Constraints Are Boundaries", puts every must-not from ADRs,
  conventions, testing regime, and scope exclusions in Constraints.
- **Agent-answerability quality gate.** Eight concrete checks map each
  agent question to the story section that must answer it: Goal,
  Affected Paths, Domain Rule, Inputs, Acceptance Criteria, Verification,
  Out of Scope, and Agent Stop Conditions.
- **International readability gate.** Six checks apply to each sentence:
  no idioms, no ambiguous pronouns, short sentences, active voice,
  consistent domain terms, and abbreviations spelled out.
- **Goal column in write-epics.** The building-block inventory has a Goal
  column with one sentence of concrete behavior per expected story. Each
  EPIC has a Domain Rules subsection. It lists the invariants that seed
  each story's Domain Rule section.
- **Goal column in story-slices.** The slice table grows from 4 to 5
  columns, with a Goal column between Capability and Boundaries crossed.
- **11 section-filling instructions.** The Phase 4 story-writing skill
  (`create-backlog-stories`) gives an explicit instruction for each new
  section: Goal derivation, Domain Rule extraction, Demo as numbered
  steps, Affected Paths from a codebase survey, Inputs as a reading
  manifest, Outputs with behavioral detail, Required Behavior
  (conditional), Constraints from ADRs, Suggested Agent Plan,
  Verification from `testing.yaml`, and Agent Stop Conditions from risk
  and ambiguity.
- **Plain-language pass.** After the quality gate,
  `create-backlog-stories` rereads Goal, Domain Rule, and Demo Scenario
  for understandability before it presents the backlog.
- **Developer-agent cue migration.** The completeness check in Step 1
  uses Goal instead of Demo/Scope. The pre-existing test lookup in Step 2
  reads Inputs instead of Notes for the Implementer. For backward
  compatibility, the `#### Failure scenarios` and `#### Prior Tests`
  paths stay unchanged.
- **Testability probe.** A new mandatory step 2.5 in the create-backlog
  sequence runs between write-epics and story-slices. It writes a
  testability paragraph and an ownership table per EPIC into
  `backlog/epics.md`. It replaces the planning-time output of the former
  test-design skill.
- **Two-pass TDD model.** The developer-agent owns test authoring in two
  passes. Pass 1 writes acceptance-criteria tests (Red-Green). Pass 2
  invokes the `test-design` skill after GREEN for integration and
  edge-case tests. The developer-agent fills the `tests:` and
  `test-design-pass:` frontmatter fields at commit time.
- **test-design skill rewrite.** The skill runs at implementation time,
  not planning time. It reads ownership assignments from the testability
  probe, classifies owned contracts by risk class, identifies untested
  integration paths, and writes test files.
- **test-design-verify gate.** The gate checks that stories with
  test-design output have consistent `tests:` and `test-design-pass:`
  fields. It is enabled implicitly when a story contains Failure
  scenarios or Prior Tests sections.
- **Vue Best Practices skill.** A new skill gives guidance for Vue.js
  frontend implementation. The developer-agent loads it when a story's
  outputs touch `packages/server` (Vue frontend).

### Fixes

- **Stale Notes for the Implementer references.** The references are
  removed from the story template, all four create-backlog skills, and
  the developer-agent. Inputs, Constraints, or Verification take their
  place, as fits.
- **Quality gate count.** The parent skill states "Two quality gates"
  (Agent-Answerability and International Readability), not three.
- **Story template stray fences.** Trailing empty code fences are removed
  from the template body.
- **Dispatch script scope.** Out-of-scope changes to the dispatch script,
  made during implementation dispatch, are reverted.
- **User-prompt questions restored.** The prompts for MoSCoW priorities,
  missing stories, and dependency reordering are back in
  `create-backlog-stories`. The skill rewrite had removed them by
  accident.
- **Hook search string.** `block-dangerous-git.sh` uses the correct
  search string.
- **Reconciliation test traceability.** The reconciliation agent audits
  the `tests:` field and checks contract ownership coverage.
- **Testing strategy documentation.** `testing-strategy.md` documents the
  two-pass test authoring model.

### Documentation

- **Agent-ready story format proposal.** The full proposal at
  `docs/proposals/implemented/agent-ready-story-format.md` went through
  two review rounds, and all findings are resolved.
- **Test-design layer redistribution proposal.** The full proposal is at
  `docs/proposals/implemented/test-design-layer-redistribution.md`.
- **migrate-proposal script.** A new script moves accepted proposals from
  `docs/proposals/` to `docs/proposals/implemented/`.

## 0.9.0 — 2026-09-09

This release brings concern-oriented agent context and code-first
planning. Agents find what to read by concern name, not by file path.
Planning starts from the codebase as ground truth and derives stories as
deltas from existing code to specified capabilities.

### Features

- **Concern-oriented agent context.** A single CLI-agnostic markdown file,
  `docs/agent-context.md`, replaces the four YAML agent-context files
  (`stack.yaml`, `workflow.yaml`, `governance.yaml`,
  `reading-guides.yaml`). Agents find project-native knowledge
  (supplementary specs, ADRs, handbooks, architecture views) through
  concern sections with `Read:` paths. Concerns fall into three
  categories: cross-cutting (always active), technical (per story), and
  domain (per story). Factory-canonical artifacts (`scope-map.md`,
  `.feature` files, `testing.yaml`) keep concrete paths.
- **concern-lint.** The new deterministic linter replaces `context-lint`.
  It runs four checks: CTX-SECTIONS (category headings and Read paths),
  CTX-PATHS (file resolution), CTX-REFS (the story concern vocabulary
  matches the registry), and CTX-LEGACY (flags residual YAML files).
- **Concern declarations in story frontmatter.** The planning agent writes
  `concerns: {domain: [...], technical: [...]}` into each story. The
  developer and implementation agents follow the matching sections in
  `agent-context.md`.
- **capture-context rewrite.** The greenfield (`--init`) and brownfield
  (`--init --scan`) modes write concern sections instead of YAML files.
  The skill detects the old YAML format and offers an interactive
  migration.
- **update-context retired.** The skill body is a deprecation notice. It
  points to editing `agent-context.md` directly.
- **testing.yaml relocated.** The file moves from
  `docs/agent-context/testing.yaml` to `docs/testing.yaml`. The
  resolution chain in `concern-lint`, `detect-test-regime`, `crap-score`,
  and all agent definitions follows the move.
- **Code-first planning.** The planning agent and all five backlog skills
  are reworked. The new principle "Code Is Ground Truth" starts planning
  from the codebase as it stands, not from an aspirational architecture.
  EPIC decomposition is the delta between existing code and specified
  capabilities. Step 0 (codebase survey) becomes the foundation, and
  Step 1 becomes a gap analysis.
- **Concern-routed inputs.** The planning agent and skills find
  project-native knowledge through the concern sections of
  `docs/agent-context.md` instead of hardcoded file paths. Technical
  concerns route to source directories, architecture views, and
  conventions. Domain concerns route to supplementary specs and domain
  vocabulary.
- **Agent definitions updated.** Concern references replace the lists of
  project-native files in requirements-agent, architecture-agent,
  architecture-review-agent, qa-agent, spec-review-agent,
  developer-agent, implementation-agent, virgil, and reconciliation-agent.

### Fixes

- **spec-lint required artifacts.** `prd.md` and
  `supplementary_specs/validation-rules.md` leave `REQUIRED_ARTIFACTS`,
  because the current requirements workflow produces neither. The tests
  are updated.
- **dispatch-ledger path.** The path reference in `rules.md` is corrected.
- **Reconciliation findings.** The release resolves 16 RECON findings
  from the concern-oriented context implementation.
- **QA findings.** The hook resolves `testing.yaml` correctly, and
  `concern-lint` returns the correct exit code.

### Documentation

- **Writing rules.** The writing conventions add "international team
  English".
- **Concern-oriented context proposal.** The full proposal at
  `docs/proposals/factory-concern-oriented-agent-context.md` went through
  two review rounds, and all findings are resolved.

## 0.8.0 — 2026-09-08

This release brings progressive fitting and session continuity. The
minimum-viable fitting interview drops from 19 questions to 6. The session
menu shows navigation aids. The conflict between the VIRGIL persona and
the playbooks is resolved. Fitting state is derived from tracked
artifacts, so a collaborator who clones a fitted repo inherits the team's
fitting decisions.

### Features

- **Minimal fitting pass.** `capture-context --init --scan --minimal`
  limits the interview to 6 questions: languages, frontend/backend
  frameworks, testing, running locally, and branching model. The
  remaining fields get `deferred: "full context pass pending"`, and an
  optional full pass completes them. `--init --minimal` (without
  `--scan`) covers greenfield projects.
- **Artifact-derived fitting state.** On every run, `init-factory`
  re-derives four of the five fitting keys (`fingerprint_confirmed`,
  `agent_context_populated`, `test_regime_detected`, `hooks_decided`)
  from tracked artifacts (`docs/agent-context/`,
  `.pre-commit-config.yaml`, `config/project-context.json`). A
  collaborator who clones a fitted repo and runs `init-factory` inherits
  the team's fitting decisions instead of seeing every key reset to false.
  `model_matrix_configured` lives only in the cache, because
  `config/model.conf` is gitignored and user-specific.
- **Fitting progress display.** When `fitting.status` is `"fitting"`,
  the AGENTS.md orientation file counts completed and remaining steps and
  offers to resume or skip. A note says that the summary trusts the
  cached values. It suggests `init-factory --update .` after pulls to
  reconcile.
- **Session menu descriptions.** Each B-menu playbook entry shows a
  one-line description from the playbook's opening paragraph. A footer
  hint names `explain-concept`. The `?` option launches a guided-tour
  skill for reorientation.

### Fixes

- **VIRGIL persona transition.** VIRGIL's boundaries section has an
  exception clause. When a playbook is selected, the model drops the
  VIRGIL persona and follows the playbook's operational procedure. So
  VIRGIL's "MUST NOT write code" boundary no longer blocks playbook
  execution.
- **`_fitting_status` missing-key safety.** The function uses
  `.get(k, False)` instead of direct key access. A hand-edited
  `project-context.json` with missing fitting keys then raises no
  `KeyError`.
- **`_reconcile_project_context` conditional write.** The function writes
  `project-context.json` only when a derived key changed, so it does not
  touch the file without need.
- **Minimal interview defer removed.** The 6 minimal fields do not offer
  "defer" as an action. All 6 must be answered, as the design intends.
- **Session menu qa-agent format.** The entry uses the
  `name: description` style of all other B-menu entries.
- **`dispatch_lib` YAML document marker.** `_stdlib_load` skips `---`
  lines instead of reading them as key-value pairs.

### Documentation

- **`_parse_simple_yaml_mapping` docstring.** The docstring documents a
  known limitation: comment stripping via `split('#')` does not respect
  quoted strings.
- **virgil.md line-break fix.** A mid-sentence line break in the minimal
  fitting step description is corrected.

## 0.7.0 — 2026-09-07

This release hardens the update path. The user-facing reference now
documents what the scripts do.

### Features

- **Update-factory modification detection.** `update-factory` compares
  the installed `factory/` against per-file SHA-256 checksums recorded at
  install time (`.agent-factory/factory-checksums.json`). It reports each
  modified, added, and removed file. The update stops with exit 2 when it
  detects user changes. `--force` keeps changed files under
  `.agent-factory/factory-user-changes/<timestamp>/` and continues.
  `--check` reports without touching anything. On failure, a rollback
  restores the previous `factory/` automatically.
- **`--add` / `--remove` CLI management.** These flags add or remove CLI
  wiring after install, without a full reinstall. The wiring covers
  dot-directories, symlinks, guardrails, step guards, usage capture,
  freshness hooks, and generated agents. The root `init-factory` wrapper
  forwards `--add` and `--remove` to the underlying script.

### Fixes

- **step-guard bail-early.** The guard checks that it exists and that jq
  is available before it parses stdin and the event. Missing
  infrastructure then exits 0 instead of crashing the session with "hook
  errored".

### Documentation

- **README reference tables expanded.** Both scripts get CLI flag tables.
  The "What init-factory creates" table grows from 8 to 16 rows. The new
  rows cover step guard hooks, freshness check, usage capture hooks,
  generated agents, hook config, project-context.json, test regime, usage
  runtime, usage lifecycle, and install checksums.
- **Factory guide expanded.** The section "What init-factory put on your
  disk" adds `config/project-context.json` and
  `docs/agent-context/testing.yaml`. The section "Updating it again"
  documents `--check`, `--force`, and `--add`/`--remove` with code
  examples. A new troubleshooting entry repairs a dangling `origin/HEAD`.
- **Install section rewritten.** Separate subsections explain wrapper
  delegation, the update workflow, and adding or removing a CLI.

## 0.6.0 — 2026-09-07

This documentation release covers the step from running `init-factory` to
starting the first playbook. It also hardens the hooks and the rulebook
for daily use.

### Features

- **Factory-freshness check.** A new hook warns on the first tool call of
  each session when the installed `factory/` is out of sync with
  `packages/factory/`. It never blocks. It exists for all CLIs: a bash
  hook (Claude/Copilot/Codex), a TypeScript extension (Pi), and a Copilot
  hook config. `init-factory` stamps the tree hash, and `update-factory`
  refreshes it.

### Fixes

- **step-guard: no manifest, no restriction.** The guard checks for a
  loaded step manifest before it rejects an empty path. Without a
  manifest, it imposes no restrictions. So sessions without
  `.current-work/current-step.yml` are not blocked. A debug dump records
  path-extraction misses.
- **Codex skill resolution path.** The INDEX.yaml resolution example in
  the rulebook names `.agents/skills/`, where init-factory installs
  skills, instead of `.codex/skills/`.

### Documentation

- **Onboarding bridge.** Getting Started explains what `init-factory` put
  on disk: `project-context.json`, `model.conf`, and `agent-context/`. A
  newcomer then knows these files when a playbook references them.
  Context becomes the fifth vocabulary entry. INDEX.yaml is presented as
  a human reference as well as a machine lookup.
- **Newcomer tour expanded.** The tour covers the config artifacts and the
  fitting session. VIRGIL knows about the model matrix in greenfield
  projects.
- **READMEs refreshed.** The root and `packages/factory/` READMEs describe
  the current structure.
- **Nine broken doc links repaired.** `orchestrator/` becomes
  `packages/orchestrator/`, `tests/orchestrator/` becomes
  `tests/factory/`, and `spec/use_cases/` becomes
  `~archive/spec/use_cases/`. One dead README anchor is removed.

## 0.5.0 — 2026-09-07

This is the first versioned release. `factory/VERSION` holds the factory
version, and the install manifest records it in the `factory_version`
field of `.agent-factory/factory-install.json`.

### Features

- **Fitting lifecycle.** When init-factory runs against an existing
  codebase, it scans for languages, frameworks, package managers, CI,
  linters, test runners, and docs structure. The results go into
  `config/project-context.json`, with a fitting state that tracks what is
  confirmed.
  - **Brownfield projects** get `fitting.status = "unfitted"`. The first
    session offers a guided fitting. It confirms the scan, fills the agent
    context, configures the model matrix, and decides on hooks.
  - **Greenfield projects** (no signals detected) get
    `fitting.status = "greenfield"` and skip the fitting.
  - Fitting progress persists across sessions. The next session resumes
    where the last one stopped.
- **Selective CLI wiring.** `init-factory` asks which CLIs you use and
  wires only those. Pass `--cli claude copilot` or choose interactively.
  Add a CLI later with `init-factory --add copilot`, and remove one with
  `init-factory --remove pi`.
- **One-hop orientation.** The CLI orientation file (`AGENTS.md` /
  `CLAUDE.md` / `copilot-instructions.md`) holds everything the model needs
  for its first turn. It checks the fitting state and presents the session
  menu without pointing to a second file. A weak model that reads only the
  orientation file still behaves correctly. VIRGIL becomes optional
  enrichment instead of the mandatory session persona. A strong model that
  follows the link to `virgil.md` gets richer guidance. A weak model skips
  it and still works.
- **Model matrix.** `config/model.conf` holds stanzas for the installed
  CLIs only, with `CONFIGURE-ME` placeholders instead of real model IDs.
  Its howto header gives model ID examples per CLI and explains how to
  validate them. Step 0 of VIRGIL's fitting walks through the
  configuration.
- **Orientation non-interference.** init-factory never overwrites an
  existing instruction file. It handles four cases. Where no file exists,
  it creates a symlink. It skips its own symlink and leaves a foreign
  symlink alone. Into an existing file, it prepends a marker-fenced block.
  `remove-factory` reverses all four cases.
- **Hooks.** `step-guard.sh` exits 0 when `factory/scripts/step-guard` is
  absent, as in a fresh clone or a partial install. In a brownfield
  project with an existing `.pre-commit-config.yaml`, the hooks are not
  merged automatically. The fitting session handles the merge.
- **Monorepo.** The product source lives under `packages/factory/`. The
  root `factory/` is the installed copy, which git ignores and
  `update-factory` syncs. The root `init-factory` is a thin wrapper.

### Documentation

- The README is rewritten. It contrasts the project before and after
  installation, states reversibility as a promise, and mentions fitting
  for brownfield projects.
- All eight doc gaps on the newcomer path are closed: model matrix,
  tiers, stale ruff refs, project.json, directory layout, factory README,
  and agent context.
- The pre-commit hook comments are rewritten for clarity.
- "Operator" becomes "user" across 127 files.
- An editorial pass covers all 58 skills.
- The init-factory proposal documents the orientation architecture.
