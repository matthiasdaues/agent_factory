# Factory-to-Miro ETL

`generate.py` derives navigable Miro SVG layouts from the Factory's declared
agents, skills, playbooks, and artifact contracts. The generated map is a view
of Factory content, not a second process definition.

## Run the ETL

Run the generator from any working directory:

```bash
uv run --script poc/workflow/miro-generator/generate.py \
  --factory-root packages/factory \
  --output-dir /tmp/factory-miro
```

Check an existing output without changing it:

```bash
uv run --script poc/workflow/miro-generator/generate.py \
  --factory-root packages/factory \
  --output-dir /tmp/factory-miro \
  --check
```

The check exits with status 1 and names every missing or stale generated file.

## Extract

The ETL reads these canonical sources:

- [`INDEX.yaml`](../../../packages/factory/INDEX.yaml) for the Factory inventory
  and ordered playbook agent sequences;
- agent frontmatter for skills, required inputs, context inputs, and outputs;
- skill frontmatter for declared inputs and outputs;
- playbook `steps` frontmatter when a playbook declares step contracts.

The ETL does not infer control flow from Markdown prose. A missing declaration
becomes a diagnostic instead of an invented relationship.

## Transform

The normalized model connects producers and consumers through artifact paths:

```text
producer -> artifact -> consumer
```

Relationships use three confidence levels:

- `exact`: normalized patterns are equal. A placeholder such as `{name}`
  normalizes to `*`.
- `certain`: one side is an exact path that matches the other side's glob.
- `possible`: two compatible globs may overlap.

Possible relationships use dashed connectors. The diagnostics file lists them
separately so a reader never mistakes them for declared exact dependencies.

Playbook routes keep only forward artifact relationships between agents in the
playbook's declared sequence. Machine-readable playbook steps receive their own
step-level artifact graph.

## Load

Each run writes:

- `factory-map.json`: the normalized source-derived model;
- `factory-map-diagnostics.json`: missing contracts, unresolved skills, broad
  patterns, and possible relationships;
- `overview.svg`: one node per playbook;
- `artifacts.svg`: agents and contracted skills connected through artifacts;
- `playbooks/<name>.svg`: one detail view per playbook;
- `generation-manifest.json`: the files owned by the ETL.

The SVG files use Miro's `data-content`, `data-source`, `data-start`,
`data-end`, and `data-arrow` attributes. They remain valid SVG and can be
checked by ordinary XML tools.

## Relationship to the prototype generators

The older scripts in this directory remain as visual experiments:

- `detail.py` stores a hand-maintained process graph.
- `layout.py` lays out that graph.
- `artifacts.py` stores a second hand-maintained artifact mapping.
- `overview.py` and `eight.py` provide alternate compositions.
- `colors.py` targets hard-coded Miro widget IDs.
- `split.py` splits the former detail board into Miro-sized batches.

`generate.py` does not import those models. Its output changes only when the
Factory declarations or the ETL change.

## Verify

Run the focused contract suite:

```bash
uvx --with pyyaml pytest tests/factory/test_miro_factory_etl.py -q
```

The suite covers exact and possible artifact relationships, skill bindings,
skill contracts, playbook route filtering, step contracts, SVG validity,
deterministic drift checks, and the current Factory inventory.
