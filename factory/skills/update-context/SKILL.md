---
name: update-context
description: >-
  Update a field in docs/agent-context/*.yaml as decisions emerge. Writes
  inline values directly when mode: primary; writes name and source together
  when mode: index, refusing any write that lacks a source pointer. Records
  deferred decisions as deferred: "reason" and proposes creating
  reading-guides.yaml on the first source pointer. Invokable by any agent
  during any phase.
category: utility
version: 1.0.0
---

# Update Context

Actively update `docs/agent-context/*.yaml` as decisions emerge across
phases — recording a technology choice, a workflow practice, a governance
rule, or a deferral directly into the field it belongs to. Merely *reading*
the index files for context is not this skill; any agent can do that. This
skill is for *changing* them.

See
[Agent Context Composition](../../rulebooks/conventions/agent-context-composition.md)
for the binding structural rules this skill follows, and
[ADR-0014](../../../docs/adr/0014-two-layer-routing-with-two-mode-lifecycle.md)
for the lifecycle rationale.

`capture-context` scaffolds the three Layer 2 index files and fills their
first values for a greenfield project. `update-context` is every write after
that — the sole write path once an index file carries `mode: index`
(hand-editing an index file in that mode is forbidden).

## When to use this skill

Use this skill when:

- A technology, workflow, or governance decision has been made and belongs
  in `stack.yaml`, `workflow.yaml`, or `governance.yaml`.
- A decision needs a `source:` pointer added once a handbook, ADR, or
  convention document now records it.
- A decision is not yet ready to record and needs to be marked
  `deferred: "reason"`.

Do not use this skill to read the index files for context — read them
directly. Do not use it to flip a file's `mode` from `primary` to `index`;
the bulk mode transition is a separate concern from a single field write.

## Agent-context structure

Three Layer 2 index files under `docs/agent-context/`: `stack.yaml`,
`workflow.yaml`, `governance.yaml`. Each carries a top-level `mode` field —
`primary` or `index` — and a set of leaf fields addressed by dotted key path
(e.g. `stack.yaml#frameworks.backend`). Most leaf fields are plain scalars in
the template (`backend: null`); a few, such as `stack.yaml#languages`, are
already structured as a list of mappings (`name`, `version`, `role`,
`source`) because they can hold more than one entry. The write patterns
below apply to both shapes — the only difference is whether the target is
the whole leaf or one sub-key inside an existing mapping.

## Workflow

### 1. Read the current state

Read the target index file and locate the field by its dotted key path. Note
the file's top-level `mode` and the field's current value (`null`, a scalar,
a `{name, source}` mapping, or a `{deferred}` mapping).

### 2. Choose the write pattern

Apply these rules in order — the first one that matches decides the write:

1. **Deferring a decision** → write `deferred: "<reason>"` and go to
   [Deferred fields](#deferred-fields). This replaces whatever was at the
   field, in either mode.
2. **A source pointer is being recorded** (the operator supplies both the
   value and a `source:` path, in either mode) → write
   `name:` and `source:` together. See
   [Writing name and source together](#writing-name-and-source-together).
3. **No source pointer, `mode: primary`** → write the inline value directly.
   See [Writing inline values](#writing-inline-values).
4. **No source pointer, `mode: index`** → refuse the write. See
   [Refusing writes without a source](#refusing-writes-without-a-source).

#### Writing inline values

`mode: primary` means the index file is the primary source of the decision
— no `source:` pointer is required, or permitted, yet. Write the value
directly to the field:

```yaml
frameworks:
  backend: FastAPI 0.100
```

For a structured field (`languages`), fill the value sub-keys (`name`,
`version`, `role`) and leave `source: null`.

#### Writing name and source together

Once a decision has an authoritative document to point at — a handbook
section, an ADR, a convention file — record both the name and the pointer
together. Never write one without the other:

```yaml
frameworks:
  backend:
    name: Django
    source: docs/adr/015-switch-to-django.md
```

For a structured field, fill `name` and `source` (plus `version`/`role`
where applicable) on the existing mapping.

A `source:` pointer prefers the project-local convention document over a
factory rulebook default when both describe the same decision.

After this write, check the
[reading-guide creation trigger](#reading-guide-creation-trigger).

#### Refusing writes without a source

`mode: index` means the index file is a downstream routing table — every
non-null, non-deferred leaf must carry a `source:` pointer. Reject any write
that would leave a field with an inline value, or a `name` without a
`source`, once the file is in this mode. Tell the requester which field was
rejected and that a `source:` pointer is required; do not partially write
the name and leave the source for later.

This refusal applies regardless of who is attempting the write — an
operator hand-editing the file or another agent — because `update-context`
is the sole write path once a file carries `mode: index`.

#### Deferred fields

Write `deferred: "<reason>"` as the **sole key** at the field's leaf
position. Discard whatever was previously there — a `null`, a scalar value,
or a `{name, source}` mapping:

```yaml
data_stores:
  deferred: "evaluating options"
```

`deferred` must never coexist with `name` or `source` in the same mapping —
`context-lint` flags that combination as a `CX-KEYS` error. A deferred field
is excluded from the primary-to-index transition condition; it is a
conscious choice to postpone, not a defect.

### 3. Reading-guide creation trigger

After any write that adds a `source:` pointer (step 2, pattern 2), check
whether `docs/agent-context/reading-guides.yaml` exists. If it does not,
propose creating it from
`factory/rulebooks/templates/context-reading-guides.yaml` — this is the
first source pointer the project has recorded, and the reading guide only
becomes useful once there is a populated section to route to. On
confirmation, copy the template unchanged (it ships with sensible default
concerns — `backend`, `frontend`, `testing`, `architecture`, `packaging` —
that a project can prune or extend). Do not create it silently; the operator
decides whether to accept the proposal now or later. If the file already
exists, do nothing here.

### 4. Validate

Run `factory/scripts/context-lint` and confirm zero errors. In particular:

- `CX-KEYS` — a `deferred` key must not coexist with `name` or `source`.
- `CX-SRC` — a `mode: index` field with a `name` must also have a `source`.
- `CX-SRC-EXIST` — a `source:` pointer must resolve to a real file on disk.

Fix the write before proceeding if any of these fire; a warning-level
`CX-NULL` on an unrelated field is expected and not a blocker.

### 5. Commit

Commit the change with format:

```
docs: update agent context <file> — <field> (<ID>)
```

Where:

- `<file>` is `stack.yaml`, `workflow.yaml`, or `governance.yaml`
- `<field>` is the dotted key path (e.g. `frameworks.backend`)
- `(<ID>)` is the story, ADR, or phase context that triggered the update
  (e.g. `(ST-0042)`, `(ADR-0015)`)

When no ID applies, omit the suffix:

```
docs: update agent context <file> — <field>
```

One commit per update (a reading-guide creation accepted in the same turn
may ride in the same commit as the source-pointer write that triggered it).

## Example

**Scenario:** `stack.yaml` is `mode: primary`. The operator settles on
FastAPI for the backend, then later points it at the ADR that recorded the
choice.

**Workflow:**

1. Operator states the decision: FastAPI 0.100 for the backend, no source
   yet. Read `stack.yaml`, locate `frameworks.backend` (currently `null`),
   confirm `mode: primary`.
2. No source pointer, `mode: primary` → write the inline value:
   `backend: FastAPI 0.100`.
3. Run `context-lint`, confirm zero errors.
4. Commit: `docs: update agent context stack.yaml — frameworks.backend (ST-0042)`.
5. Later, the operator adds `docs/adr/004-use-fastapi.md` as the source.
   Read `stack.yaml` again, confirm the field still resolves.
6. A source pointer is being recorded → write
   `backend: {name: FastAPI, source: docs/adr/004-use-fastapi.md}`.
7. Check the reading-guide trigger: `docs/agent-context/reading-guides.yaml`
   does not exist → propose creating it from the template. Operator
   confirms → copy the template unchanged.
8. Run `context-lint`, confirm zero errors.
9. Commit: `docs: update agent context stack.yaml — frameworks.backend (ADR-0004)`.

## Cross-referencing

Do not add `docs/agent-context/*.yaml` to agents' `outputs:` — this skill
owns the write target. If another agent needs to reference an index-file
entry, link to it with the `<file>#<dotted.key.path>` convention (e.g.
"See `stack.yaml#frameworks.backend`.").

## Mode transition — primary to index

When a field write completes (any write pattern except deferral), check the
transition condition across all three index files. The transition is
operator-confirmed and one-directional — once in index mode, files do not
revert to primary.

### Transition condition

Walk the YAML structure of `stack.yaml`, `workflow.yaml`, and
`governance.yaml`. Classify each leaf field as one of:

- **null** — no value recorded. Excluded from the condition.
- **deferred** — has `deferred: "<reason>"`. Excluded from the condition.
- **valued** — has an inline value, a `{name, source}` mapping, or a
  `{name}` mapping. Included in the condition: must have a `source:` pointer.

The transition condition is met when **every valued leaf across all three
files has a `source:` pointer**. Null and deferred fields do not block it.

### Prompt and execution

When the transition condition is met and all three files are still
`mode: primary`:

1. Tell the operator: "All context fields now have sources. Switch to index
   mode?"
2. If the operator **declines**: leave all three files in `mode: primary`.
   Do not prompt again until another field write changes the state.
3. If the operator **confirms**: execute the atomic flip.

### Atomic flip

In a single commit:

1. Set `mode: index` in all three files.
2. Strip inline values to names only — convert any bare scalar value
   (e.g. `backend: "FastAPI 0.100"`) to a `{name, source}` mapping
   (e.g. `backend: {name: FastAPI, source: docs/adr/004.md}`). Fields
   already in `{name, source}` form are left as-is.
3. Preserve all `source:` pointers unchanged.
4. Preserve all `deferred:` fields unchanged.
5. Leave `null` fields as `null`.

Commit message:

```
docs: transition agent context to index mode
```

### Post-transition validation

Run `factory/scripts/context-lint` — confirm zero errors. In particular:

- `CX-MODE` — all three files report `mode: index`.
- `CX-SRC` — every non-null, non-deferred field has a `source:` pointer.

### Transition not offered

Do not prompt for transition when:

- Any file is already `mode: index` (the transition is complete).
- A valued leaf lacks a `source:` pointer (the condition is not met).

## Validation reference

| Script                         | Mode    | Checks                                                                                                                                |
| ------------------------------ | ------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `factory/scripts/context-lint` | default | files exist, YAML parses, required keys present, `mode` is valid, null leaves warn, `deferred` conflicts, `source` presence/existence |
