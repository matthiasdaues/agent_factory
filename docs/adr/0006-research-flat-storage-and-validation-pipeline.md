---
id: 0006
status: proposed
evaluation: none
---

# Research artifacts use flat, prefixed rulebook storage and a schema → policy → semantic validation pipeline

## Context

The falsification-driven research feature adds a sixth family to the factory catalog: four agents, six skills, one playbook, four policies, ten artifact templates, and ten JSON Schemas. It also adds two deterministic validator scripts. Three structural questions had to be answered, and each was decided against the obvious first guess, so each is recorded here.

**Where do the research rulebook files live?** The catalog already groups rulebooks by kind — `rulebooks/conventions/` for prose conventions, `rulebooks/templates/` for artifact skeletons. A feature this size invites a per-feature subtree — `rulebooks/research/conventions/`, `rulebooks/research/templates/`, and so on — to keep its files together.

**How are research artifacts validated?** A research run produces JSON artifacts (briefs, plans, conjectures, source records, test records, reviews, votes, a claim register, a final report) that must be checked before each playbook step proceeds. Some checks are purely structural (required fields, types, enums, identifier patterns); some enforce cross-artifact policy (role separation, quorum, current claim versions); and some are irreducibly semantic (is the evidence convincing, is a source truly independent, was a test severe). Bundling all three into one validator, or leaving them all to an agent's judgment, were both on the table.

**Where does research sit in the phase model?** The factory's agents carry a `phase` number, from phase 1 (Requirements) through phase 5 (Quality), plus phase 0 (Utility). Research does not fit inside the linear idea → production chain those phases describe.

## Decision

**Flat storage with a `research-` filename prefix, not a per-feature subtree.** Every research rulebook file lives directly in the existing by-kind directory and is named with a `research-` prefix: policies as `rulebooks/conventions/research-*.md`, templates as `rulebooks/templates/research-*.md`, schemas as `rulebooks/schemas/research-*.schema.json`. The by-kind grouping stays the single axis of organisation; the prefix, not a directory, marks the family. This is the direct application of YAGNI and of the catalog's existing shape: `index-lint` derives a rulebook's `category` from its parent directory, so the four research policies index as `conventions` (their own frontmatter reads `category: policies`, a documentation label describing their nature, not a directory that exists). A per-feature subtree would have forked the organising axis for one feature and broken the directory-derived category that `index-lint` depends on.

**A new `rulebooks/schemas/` category holding JSON-Schema data, deliberately outside `INDEX.yaml`.** The research artifacts are validated against machine-readable JSON Schemas, a genuinely new kind of rulebook — data contracts, not prose conventions or fill-in templates. They get their own `rulebooks/schemas/` directory. `index-lint` scans Markdown frontmatter only, so the `.schema.json` files are intentionally absent from `INDEX.yaml`: they are consumed by the validator scripts, not resolved by name the way agents, skills, and prose rulebooks are.

**A three-stage validation pipeline, schema → policy → semantic, split by whether a machine can decide.** Validation is layered by decidability, not bundled:

- **Stage 1 — schema** (`factory/scripts/schema-validate`): a stdlib-only JSON-Schema validator. Purely structural — required fields, types, enums, identifier patterns, timestamp formats, array minimums. The load-bearing gate every later stage assumes.
- **Stage 2 — policy** (`factory/scripts/policy-validate`): a stdlib-only validator for the *enforceable* half of the four research policies — role separation, cross-artifact references, quorum, current claim versions. It reads across a set of related artifacts. Its `--pipeline` mode runs stage 1 then stage 2 in order and stops at the first failing stage.
- **Stage 3 — semantic**: the judgment a script cannot make — evidence support, source independence in substance, test severity, claim atomicity. This stage belongs to a qualified human or agent reviewer.

The order is fixed and progression blocks on the first failing stage. This is the direct application of the standing "Agentic Creation, Deterministic Validation" principle: mechanise every check that can be mechanised (stages 1 and 2), and name the residue that cannot (stage 3) rather than pretending a script can settle it. Both scripts are stdlib-only, exactly like `spec-lint` and `arch-lint`, so they run without a virtualenv.

**Research is a phase-6 grouping, not a sixth step in the production chain.** The four research agents carry `phase: 6`, `phase_name: Research`. This is a catalog grouping for a self-contained workflow driven by the standalone `research-topic` playbook (`category: orchestration`), not an extension of the linear requirements → … → quality chain. The five-phase production chain is unchanged; research runs alongside it.

### Rejected alternatives

- **Per-feature subtree (`rulebooks/research/…`).** Keeps one feature's files visually together, but forks the catalog's by-kind organising axis for a single feature and breaks `index-lint`'s directory-derived category. The `research-` prefix gives the same locate-by-family grouping (`ls rulebooks/conventions/research-*`) without either cost. Rejected as premature structure.
- **One combined validator, or all-agent validation.** A single validator would weld the deterministic structural/policy checks to the semantic judgment a script cannot make, muddying the trust boundary the whole factory rests on. Leaving everything to an agent abandons determinism where it is cheap and reliable. The staged split keeps stages 1–2 mechanical and reproducible and names stage 3 honestly. Rejected.
- **Index the schemas in `INDEX.yaml`.** Would require teaching `index-lint` to parse JSON, and for no benefit: schemas are resolved by path from the validator scripts, never looked up by catalog name. Rejected as scope creep.

Once "keep the catalog's existing conventions, mechanise what is mechanisable, and add nothing speculative" is held fixed, no genuine second contender remains for any of the three sub-decisions, so no Pugh Matrix applies (`evaluation: none`).

## Consequences

**Positive**

- The research family obeys the catalog's existing conventions: by-kind directories, directory-derived categories, `research-` as a greppable family marker. Nothing new to learn to navigate it.
- The trust boundary is explicit: stages 1 and 2 are deterministic gates with exit codes; stage 3 is named as human/agent judgment, not smuggled into a script.
- `schema-validate` and `policy-validate` are stdlib-only and subprocess-friendly, runnable on demand or from the research skills and agents, no install required.

**Negative / risks**

- The `category: policies` frontmatter on files that `index-lint` categorises as `conventions` is a deliberate but latent inconsistency; a reader who trusts the frontmatter over the directory will be misled until they read this record.
- The `research-` prefix relies on discipline: nothing mechanically enforces that a new research rulebook carries the prefix, where a directory would have.
- The `.schema.json` files sit under `rulebooks/` yet never appear in `INDEX.yaml`; a reader expecting the catalog to list every rulebook file will not find them, by design.

## Referenced from

- [09_architecture_decisions.md](../09_architecture_decisions.md)
- [factory/playbooks/research-topic.md](../../factory/playbooks/research-topic.md)
- [factory/docs/factory-guide.md § Rulebooks](../../factory/docs/factory-guide.md#rulebooks)
- [05_building_block_view.md § 5.2.2](05_building_block_view.md#522-research-artifact-validators-schema-validate-policy-validate)
