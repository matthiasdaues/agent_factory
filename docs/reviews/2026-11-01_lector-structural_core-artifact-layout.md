# Lector structural pass: Core Artifact Layout

- document: `docs/proposals/core-artifact-layout.md`
- commit: `088bfff7` on `dev`
- mode: structural pass, cut plan only; the proposal is unchanged
- protected: the frontmatter, the Primer placeholder, and the Appendix tables

Approve or reject each numbered item. Line numbers refer to the proposal at
commit `088bfff7`. After approval, the lector applies the approved items and
runs a sentence pass over the changed sections.

## 1. Order

**O-1. Explain the non-core homes before the path table.** The folder
`areas/` and the removal of the use-case files first appear as rows of the
path table (lines 164 and 166). The text that explains them follows the table
(lines 168-178). So the reader meets the list before its map, and the heading
"Path table" does not predict the reasons below it. Proposed change:

- Add the heading `### Files outside the core` after "The core artifact set".
- Move lines 121-126 (working output, arc42 prose, `testing.yaml`,
  `agent-context.md`) under it.
- Move lines 168-173 (todo lists, area specs) and lines 175-178 (actor-goal
  list, use-case files) under it.
- "Path table" then holds only line 144 and the table.

Proposed order of `## Design`:

1. `### The core artifact set` (lines 100-119)
2. `### Files outside the core` (new, from lines 121-126, 168-178)
3. `### Routing and vocabulary` (lines 130-140)
4. `### Path table` (lines 144-166)
5. `### The migration script` (lines 182-201)
6. `### Factory changes` (lines 205-208, plus item C-4)

**O-2. Give the use-case fallbacks a home in the design.** Scope line 216-217
removes the use-case fallbacks from `developer-agent` and
`reconciliation-agent`. No design section mentions them, so Scope introduces
new content. Item C-4 adds one sentence to "Factory changes". The Scope
bullet stays.

## 2. Duplicates

**D-1. The old routing files are described twice.** Motivation line 79
states that `agent-context.md` and `CONTEXT-MAP.md` both route agents.
Routing lines 131-134 describe the old files again in the past tense
("routed before it", "listed", "pointed at"). Home: Motivation keeps the
problem. Routing states only the target. Proposed wording for lines 130-135:

> `docs/agent-context.md` is the project's one routing file (DEC-07). Each
> bounded context becomes a domain concern in it, with its description and
> `Read:` paths. The domain concerns also route to the glossary. After the
> move, `CONTEXT.md` and `CONTEXT-MAP.md` do not exist.

**D-2. The link to the entity-model proposal appears three times:**
Motivation lines 83-86, Design lines 118-119, and Scope lines 224-226. Home:
the Scope deferral. Lines 118-119 stay, because they explain the "none yet"
gates in the table. Motivation shrinks to one sentence, as item R-1 shows.

## 3. Record

**R-1. History and a reversed fact in Motivation, lines 83-86.** "It was
split off this proposal so that each can be reviewed on its own" is record
text, and it reverses the direction of the split (see contradiction K-5).
DEC-01 already holds the decision. Proposed wording for the paragraph:

> The proposal `[entity-model-as-dbml.md](entity-model-as-dbml.md)` needs one
> canonical path for its DBML file in every project (todo T-0006). It builds
> on this layout, which ships first (DEC-01).

**R-2. History word in line 176-177.** "No factory step produces them since
ST-0098" tells when the change happened. Proposed: "No factory step produces
them (ST-0098)." The story reference stays.

**R-3. DEC-06 is never cited.** The script name at line 182 is the decision
DEC-06 holds. Proposed: append "(DEC-06)" to the first sentence of "The
migration script".

No decision stamp or date sits in the target-state text. Open Questions holds
"None", which is correct. The file already follows the Appendix layout of the
proposal template.

## 4. Blocks to cut or shrink

No block is cut. Each section serves the reader who plans the stories. The
savings come from items D-1, D-2, and R-1, about 40 words in all.

## 5. Inbound links

`grep -rn "core-artifact-layout.md#" docs` finds no anchor link. Two files
name the proposal: `docs/spec/todo.md:105` links to the file without an
anchor, and `docs/proposals/entity-model-as-dbml.md` names it in code spans.
The new heading in O-1 and the reordered headings break no link.

## 6. Content fixes

**C-1. The Summary omits `areas/`.** Lines 63-65 name `features/`,
`schemas/`, and `work/`. The path table (line 164), Scope (line 214), and the
first completion criterion (line 237) also name `areas/`. Proposed insertion
after "payload schemas in `docs/spec/schemas/`": "area specs in
`docs/spec/areas/`,".

**C-2. The deferral list omits the todo-list merge.** DEC-09 and line 169-170
defer the merge of `todo.md` and `todos.md` to todo T-0008. Proposed bullet
under "Explicitly deferred":

> - **One todo list.** Merging `todo.md` and `todos.md` changes one ID scheme
>   and its references. Todo T-0008 holds it (DEC-09).

**C-3. The script section does not say how chapter 12 is handled.** The path
table (line 156) and line 139-140 keep chapter `12_glossary.md` as one line
that links to `docs/spec/glossary.md`. That is not a `git mv`. Proposed
sentence after line 186, for the stakeholder to confirm: "It moves
`docs/arc42/12_glossary.md` to `docs/spec/glossary.md` and writes a new
chapter 12 with one line that links to it." Contradiction K-4 must be
settled first.

**C-4. Factory changes, from Scope line 216-217.** Proposed sentence:
"`developer-agent` and `reconciliation-agent` lose their fallback to the
use-case files (DEC-10)."

## 7. Estimate

| Part              | Words now | Words after |
| ----------------- | --------: | ----------: |
| Target-state      |      1430 |  about 1450 |
| Record (Appendix) |       442 |         442 |

The additions in C-1 to C-4 outweigh the cuts in D-1, D-2, and R-1 by about
20 words.

## Contradictions for the author

The lector does not resolve these.

- **K-1. Core files in folders.** Principle line 91-92 says "A file at the
  top of `docs/spec/` is a core file. Folders hold the rest." The core table
  (lines 108 and 115) lists `features/*.feature` and `schemas/*` as core files
  in folders. The text also does not say whether an area spec in `areas/` is
  core, although it can meet the definition in line 100-102.
- **K-2. An empty `schemas/`.** The first completion criterion (lines
  235-237) expects `schemas/` after the factory's own migration. No path-table
  row moves a file there, and git does not keep an empty folder.
- **K-3. An unchanged old path.** The criterion at lines 240-241 greps for
  "every old path in the path table". The row `docs/spec/scope-map.md` is
  unchanged, so that grep cannot find nothing.
- **K-4. Glossary order in the factory repository.** The repository has both
  `docs/arc42/12_glossary.md` and `docs/CONTEXT.md`. If chapter 12 moves first,
  the script finds a glossary and stops (lines 192-194). DEC-08 says the script
  moves terms without that condition. The criterion at lines 252-254 names only
  the terms of chapter 12 and does not say whether the stop is expected.
- **K-5. Direction of the split.** Line 85 says the entity-model proposal
  "was split off this proposal". DEC-21 of `entity-model-as-dbml.md` says this
  layout was split off the entity-model proposal.
- **K-6. Boundaries.** The frontmatter names `docs/spec/todo.md`, a path that
  moves. It omits `packages/factory/scripts/migrate-spec-layout`,
  `packages/factory/agents/coaching-agent.md`, and
  `packages/factory/skills/write-prd/SKILL.md`. The last two name todo paths,
  and line 205 changes every factory file that names an old path.
- **K-7. Reference count.** Line 77 counts 7 references to
  `docs/arc42/CONTEXT.md`. `grep -rc` over `packages/factory/` counts 6 lines.
  The difference may be two hits on one line.

One naming note: `packages/factory/scripts/migrate-layout` already exists and
migrates the install layout. The new `migrate-spec-layout` is close to it in
name.
