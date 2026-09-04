---
name: update-context
description: >-
  Update a field in docs/agent-context/*.yaml as decisions emerge. Writes
  name and source together when both are available; writes inline values when
  only a value exists; records deferred decisions as deferred: "reason".
  Maintains reading-guides.yaml — creates it on the first source pointer,
  asks which concern a new key belongs to, and keeps concern assignments
  current on source changes. Invokable by any agent during any phase.
category: utility
version: 2.1.0
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
first values. `update-context` is every write after that.

## When to use this skill

Use this skill when:

- A technology, workflow, or governance decision has been made and belongs
  in `stack.yaml`, `workflow.yaml`, or `governance.yaml`.
- A decision needs a `source:` pointer added once a handbook, ADR, or
  convention document now records it.
- A decision is not yet ready to record and needs to be marked
  `deferred: "reason"`.

Do not use this skill to read the index files for context — read them
directly.

## Agent-context structure

Three Layer 2 index files under `docs/agent-context/`: `stack.yaml`,
`workflow.yaml`, `governance.yaml`. Each carries a set of leaf fields
addressed by dotted key path (e.g. `stack.yaml#frameworks.backend`). Most
leaf fields are plain scalars in the template; a few, such as
`stack.yaml#languages`, are structured as a list of mappings (`name`,
`version`, `role`, `source`) because they can hold more than one entry. The
write patterns below apply to both shapes.

## Workflow

### 1. Read the current state

Read the target index file and locate the field by its dotted key path.
Note the field's current value: a scalar, a `{name, source}` mapping, a
`{deferred}` mapping, or absent.

### 2. Choose the write pattern

Apply these rules in order — the first one that matches decides the write:

1. **Deferring a decision** → write `deferred: "<reason>"` and go to
   [Deferred fields](#deferred-fields). This replaces whatever was at the
   field.
2. **A source pointer is being recorded** (the operator supplies both the
   value and a `source:` path) → write `name:` and `source:` together.
   See [Writing name and source together](#writing-name-and-source-together).
3. **No source pointer available** → write the inline value directly.
   See [Writing inline values](#writing-inline-values).

#### Writing inline values

When only a value is available and no source document exists yet, write the
value directly to the field:

```yaml
frameworks:
  backend: FastAPI 0.100
```

For a structured field (`languages`), fill the value sub-keys (`name`,
`version`, `role`) and leave `source:` absent.

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

After this write, proceed to
[reading-guide maintenance](#reading-guide-maintenance).

#### Deferred fields

Write `deferred: "<reason>"` as the **sole key** at the field's leaf
position. Discard whatever was previously there — a scalar value or a
`{name, source}` mapping:

```yaml
data_stores:
  deferred: "evaluating options"
```

`deferred` must never coexist with `name` or `source` in the same mapping —
`context-lint` flags that combination as a `CX-KEYS` error. A deferred
field is a conscious choice to postpone, not a defect.

### 3. Reading-guide maintenance

After any write that adds a new key or changes a `source:` pointer,
maintain `docs/agent-context/reading-guides.yaml`:

#### Creation (first source pointer)

If `reading-guides.yaml` does not exist and the write added a `source:`
pointer, propose creating it from
`factory/rulebooks/templates/context-reading-guides.yaml`. Do not create it
silently; the operator decides whether to accept the proposal now or later.

#### Concern assignment (new key)

When a new key is added to any index file, ask the operator which concern
it belongs to. Present the concerns already in `reading-guides.yaml`:

> "Which concern does `<key>` belong to? Your current concerns are:
> `<list>`. Pick one, or name a new one."

Write the operator's answer immediately: add
`<file>#<dotted.key.path>` to that concern's reference list in
`reading-guides.yaml`. If the operator names a concern that does not exist
yet, create it.

#### Concern reassignment (source change)

When a `source:` pointer changes on an existing key, ask the operator
whether the concern assignment is still correct:

> "`<key>` was under `<concern>`. Source changed to `<new-source>` — still
> the right concern?"

If the operator says yes, do nothing. If they name a different concern,
move the reference.

### 4. Validate

Run `factory/scripts/context-lint` and confirm zero errors. In particular:

- `CX-KEYS` — a `deferred` key must not coexist with `name` or `source`.
- `CX-SRC-EXIST` — a `source:` pointer that looks like a file path must
  resolve to a real file on disk.

Fix the write before proceeding if any of these fire.

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

**Scenario:** The operator settles on FastAPI for the backend, then later
points it at the ADR that recorded the choice.

**Workflow:**

1. Operator states the decision: FastAPI 0.100 for the backend, no source
   yet. Read `stack.yaml`, locate `frameworks.backend` (currently absent or
   deferred).
2. No source pointer → write the inline value:
   `backend: FastAPI 0.100`.
3. Run `context-lint`, confirm zero errors.
4. Commit: `docs: update agent context stack.yaml — frameworks.backend (ST-0042)`.
5. Later, the operator adds `docs/adr/004-use-fastapi.md` as the source.
   Read `stack.yaml` again, confirm the field still resolves.
6. A source pointer is being recorded → write
   `backend: {name: FastAPI, source: docs/adr/004-use-fastapi.md}`.
7. Reading-guide maintenance: `reading-guides.yaml` does not exist →
   propose creating it from the template. Operator confirms → copy the
   template unchanged. Then ask: "Which concern does `frameworks.backend`
   belong to?" Operator says "backend" → add
   `stack.yaml#frameworks.backend` to the backend concern.
8. Run `context-lint`, confirm zero errors.
9. Commit: `docs: update agent context stack.yaml — frameworks.backend (ADR-0004)`.

## Cross-referencing

Do not add `docs/agent-context/*.yaml` to agents' `outputs:` — this skill
owns the write target. If another agent needs to reference an index-file
entry, link to it with the `<file>#<dotted.key.path>` convention (e.g.
"See `stack.yaml#frameworks.backend`.").

## Validation reference

| Script                         | Checks                                                                                     |
| ------------------------------ | ------------------------------------------------------------------------------------------ |
| `factory/scripts/context-lint` | files exist, YAML parses, null leaves are errors, `deferred` conflicts, `source` existence |
