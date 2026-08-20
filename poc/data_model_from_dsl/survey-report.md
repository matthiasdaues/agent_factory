---
title: Data-Modeling DSL Survey Report
---

# Data-Modeling DSL Survey Report

This report synthesizes forty-three recorded source records gathered for the
survey of text-based data-modeling meta-languages defined in
[research-survey-plan.json](research-survey-plan.json) and bounded by
[research-brief.json](research-brief.json). It reports what the cited sources
support. It does not rank the candidates, score them, or recommend a choice;
that decision belongs to a later Pugh Matrix and ADR.

The seven surveyed candidates are DBML, Mermaid erDiagram (the incumbent
baseline), LinkML, PlantUML IE/Chen notation, Prisma schema language, Atlas
HCL (ariga.io), and D2 with SQL table shapes.

## Findings

### Per-candidate construct expressiveness

Each candidate was tested against ten advanced constructs drawn from the
entity model: composite primary keys, JSON payload columns, enumerated string
domains, several self-referencing foreign keys on one table, nullable foreign
keys, a multi-column UNIQUE constraint not tied to the primary key, a
one-to-zero-or-one relationship, a value constraint beyond type, several
logical schemas in one database, and a cross-cutting `domain_id` convention
assertable by a validator.

**Legend:** Y = expressible. W = expressible only via workaround. N = not
expressible.

| Construct                               | DBML | Mermaid | LinkML | PlantUML | Prisma | Atlas HCL | D2  |
| --------------------------------------- | ---- | ------- | ------ | -------- | ------ | --------- | --- |
| Composite primary key                   | Y    | W       | W      | W        | Y      | Y         | N   |
| JSON payload column                     | Y    | Y       | W      | Y        | Y      | W         | W   |
| Enumerated string domain                | Y    | W       | Y      | W        | Y      | Y\*       | N   |
| Several self-referencing FKs            | Y    | Y       | Y      | Y        | Y      | Y         | W   |
| Nullable FK                             | Y    | Y       | Y      | Y        | Y      | Y         | N   |
| Multi-column UNIQUE                     | Y    | W       | Y      | W        | Y      | Y         | N   |
| One-to-zero-or-one                      | Y    | Y       | Y      | Y        | Y      | W         | W   |
| Value constraint beyond type            | Y    | W       | Y\*\*  | W        | N      | W         | N   |
| Several logical schemas in one database | Y    | N       | W      | W        | W      | Y\*\*\*   | W   |
| Cross-cutting `domain_id` convention    | N    | N       | W      | N        | N      | W\*\*\*\* | N   |

\* Atlas: two dialect-divergent shapes (inline MySQL `enum` type vs. a
separately declared PostgreSQL `enum` schema object), and value reordering is
explicitly unsupported by the migration flow once created.\
\*\* LinkML: via the `any_of`/`equals_string` boolean range-expression
mechanism, which the documentation itself flags as experimental.\
\*\*\* Atlas: the mechanism is documented and directly supports Gigacron's
four-schema split, but two open GitHub issues (#1584, #2957) show a
same-named-table collision and a silent no-op on `apply` unless every table
uses the qualified form.\
\*\*\*\* Atlas: a genuine built-in Schema Rule language exists for this class
of policy, but it is licensed exclusively to Pro/Enterprise accounts.

Full per-candidate detail, with citations, follows.

#### DBML

Composite primary keys, JSON payload columns, enumerated domains, multiple
self-referencing foreign keys, nullable foreign keys, multi-column UNIQUE, a
one-to-zero-or-one relationship, a value constraint beyond type, and several
logical schemas in one database are all expressible directly in the DBML
language reference (`docs.md`). Composite keys use `(col1, col2) [pk]` inside
an `indexes{}` block; the same block's `[unique]` setting covers multi-column
UNIQUE. JSON columns and other opaque types pass through as free text to the
target dialect. Enums use a dedicated `enum` block. Nullable foreign keys use
the default-null column setting or a `?` optional-side relationship modifier,
which also yields one-to-zero-or-one when combined with the one-to-one `-`
operator. A dedicated `checks{}` block and column-level `check:` setting
express a value constraint, though the expression itself is opaque,
dialect-specific SQL text DBML does not parse. Several logical schemas map
directly onto DBML's arbitrary `schema_name` prefix, with no documented limit
on count. Multiple self-referencing foreign keys on one table are expressible
under the general Ref grammar, though the only corroborating parser test
fixture shows two self-references on two different tables, not three on one,
so the exact cardinality Gigacron needs is inferred rather than directly
demonstrated. The cross-cutting `domain_id` convention is not expressible by
any built-in DBML mechanism.

Against the brief's MUSTs, DBML passes plain-text/version-controlled/
product-neutral, since the target dialect is chosen at `dbml2sql` generation
time rather than fixed in the source. It fails the validator MUST: direct
reading of `@dbml/cli`'s `export.ts` and `bin/dbml2sql.js` found no
`process.exit` call on a compiler error, so the process exits 0 by default
even after logging errors. It fails the Docker MUST: no official Docker image
exists on Docker Hub or GHCR for `@dbml/cli`, `dbml-renderer`, or the
`holistics/dbml` project; the only images found are unofficial, single-tag,
and stale (2019 and 2023). SVG is possible only through the unofficial
third-party `dbml-renderer`; PNG is not documented as an output format
anywhere.

DBML is licensed Apache-2.0 under single-vendor governance (Holistics
Software Pte Ltd, which also sells the commercial dbdiagram.io and dbdocs.io
products DBML feeds), with no governance charter and near-daily releases
through August 2026. DBML has a real, named, language-level `DiagramView`
construct — the closest analogue among all seven candidates to a
Structurizr-style named view — though whether any open-source renderer
honours it is unconfirmed. No official application-type generator exists.
DDL derivation via `dbml2sql` is strong and confirmed by the project's own
golden-file exporter tests for five of the ten constructs; three (self-
referencing FK, multi-column UNIQUE, one-to-one uniqueness) were not found
demonstrated in an examined fixture.

*Sources:* [source-dbml-grammar.json](sources/source-dbml-grammar.json),
[source-dbml-generation.json](sources/source-dbml-generation.json),
[source-dbml-tooling.json](sources/source-dbml-tooling.json),
[source-dbml-docker-registry.json](sources/source-dbml-docker-registry.json),
[source-dbml-licence-governance.json](sources/source-dbml-licence-governance.json),
[source-dbml-contrary-evidence.json](sources/source-dbml-contrary-evidence.json).

#### Mermaid erDiagram (incumbent baseline)

JSON payload columns and one-to-zero-or-one relationships are expressible
directly, and multiple self-referencing foreign keys and nullable foreign
keys (as of v11.16.0, released 2026-06-29) are expressible under the general
relationship grammar. Composite primary keys, multi-column UNIQUE, enumerated
domains, and a value constraint beyond type are each expressible only via
workaround: PK and UK are per-attribute labels with no grouping mechanism,
and the only place a constrained value set or a check expression could live
is an unparsed, unenforced double-quoted comment. Several logical schemas and
the cross-cutting `domain_id` convention are not expressible; the erDiagram
grammar has no schema or namespace production at all, unlike Mermaid's
classDiagram, which has a separate namespace keyword.

The single most consequential finding for Mermaid as the artifact under
replacement: direct reading of the parser's database layer (`erDb.ts`) shows
that a relationship statement naming a previously undeclared entity is not
rejected. It is silently auto-vivified into a new, attribute-less entity and
rendered as though intentional. Mermaid's ER parser therefore has no
semantic-consistency check of any kind, only lexical and grammatical syntax
checking.

Reading the actual in-repo incumbent artifact confirms this gap is not
theoretical. Only JSON payload columns and the one-to-zero-or-one
relationship are fully expressed inside the diagram itself. Enumerated
domains, nullable foreign keys, multi-column UNIQUE, and the value constraint
beyond type are carried only in the prose constraints beneath the diagram —
for example, `FOLDER_RUN.execution_context` is typed plain `string` in the
diagram, with its `SCHEDULED`/`MANUAL` domain stated only in prose. Several
logical schemas and the `domain_id` convention appear nowhere in the
artifact, diagram or prose.

Mermaid passes the plain-text/product-neutral MUST. It fails the validator
MUST: `mmdc` has no dedicated validate or lint subcommand, the only
`process.exit(1)` calls found are for CLI-usage mistakes rather than parse or
render failures, and — per the semantic finding above — a semantically
inconsistent diagram does not fail at all. It passes the Docker MUST: the
official `minlag/mermaid-cli` image is actively published and current
(pushed 2026-08-03), with SVG and PNG both documented, first-class output
formats.

Mermaid core is MIT-licensed (copyright Knut Sveidqvist); mermaid-cli carries
its own separate MIT copyright (Tyler Long). No governance charter exists;
the documented process is maintainer review plus a named individual (`knsv`)
in charge of releases, distinct from foundation governance and from
single-vendor commercial governance, since no company is documented as
controlling the core project. Being the incumbent in active use, Mermaid is
the freshest-looking candidate by construction. No named-subset-view
construct exists for erDiagram, and Mermaid has no application-type or DDL
generation of any kind.

*Sources:* [source-mermaid-erd-grammar.json](sources/source-mermaid-erd-grammar.json),
[source-mermaid-erd-syntax.json](sources/source-mermaid-erd-syntax.json),
[source-mermaid-erd-tooling.json](sources/source-mermaid-erd-tooling.json),
[source-mermaid-erd-docker-registry.json](sources/source-mermaid-erd-docker-registry.json),
[source-mermaid-erd-licence-governance.json](sources/source-mermaid-erd-licence-governance.json),
[source-mermaid-erd-incumbent-artifact.json](sources/source-mermaid-erd-incumbent-artifact.json).

#### LinkML

Enumerated string domains, multiple self-referencing foreign keys, nullable
foreign keys, multi-column UNIQUE (via `unique_keys`), one-to-zero-or-one,
and a value constraint beyond type (via the experimental `any_of`/
`equals_string` mechanism) are all expressible under the LinkML metamodel.
Composite primary keys and JSON payload columns are expressible only via
workaround: a class may declare at most one `identifier` or `key` slot, so
true composite identity is representable only as a compound `unique_keys`
constraint standing in for identity, which the documentation explicitly
states is not the same thing; and LinkML has no native opaque-JSON scalar, so
a JSON column must use `range: Any` (meant for polymorphic typed values) or
`range: string` (losing all structure semantics). Several logical schemas in
one database and the cross-cutting `domain_id` convention are each
expressible only via workaround: the SQL DDL generator's documented
algorithm maps one LinkML schema file to exactly one database schema, and
Mixins let an author compose a shared slot into every class that needs it,
but nothing checks afterward that every class in a group actually used the
mixin.

Against the MUSTs, LinkML passes plain-text/version-controlled/
product-neutral. Its validator MUST is expressible only via workaround: two
separate tools exist, and `linkml-lint` (the Schema Linter) has clean,
explicitly documented graduated exit codes (0 clean, 1 warnings only, 2 any
errors) suitable for a deterministic CI gate, while `linkml validate` (schema
and data validation against the metamodel) offers an
`--exit-on-first-failure` flag but no stated numeric exit-code contract on
failure. LinkML fails the Docker MUST: an official `linkml/linkml` image
exists and is current, but the only diagram generator, `gen-erdiagram`,
produces markdown or mermaid text only — its own documentation states
plainly that there is currently no way to generate PNG or PDF from that
output without an external, non-containerized tool.

LinkML is Apache-2.0 licensed. No governance charter was found for LinkML's
own repository; a separate linkml.io how-to guide describes a generic
steering-council governance template for other projects that adopt LinkML,
which should not be mistaken for LinkML's own governance. LinkML is not at
risk of abandonment, with a release roughly three months before retrieval.
LinkML is the only candidate in this survey with two first-party generators —
Pydantic and SQLAlchemy — plus a separate SQL DDL generator, the broadest
generation surface found, but construct survival through generation is
uneven: composite identity, opaque JSON, multi-column-unique-as-UNIQUE, and
the `any_of` value constraint are each not confirmed to survive generation,
while enumerated domains, self-referencing foreign keys, nullable foreign
keys, and one-to-zero-or-one do. No named-subset-view mechanism connects to
diagram generation.

*Sources:* [source-linkml-metamodel.json](sources/source-linkml-metamodel.json),
[source-linkml-generation.json](sources/source-linkml-generation.json),
[source-linkml-tooling.json](sources/source-linkml-tooling.json),
[source-linkml-docker-registry.json](sources/source-linkml-docker-registry.json),
[source-linkml-licence-governance.json](sources/source-linkml-licence-governance.json),
[source-linkml-contrary-evidence.json](sources/source-linkml-contrary-evidence.json).

#### PlantUML IE/Chen notation

JSON payload columns, multiple self-referencing foreign keys, nullable
foreign keys, and one-to-zero-or-one relationships are expressible directly
in the IE and Chen documentation. Composite primary keys, enumerated
domains, multi-column UNIQUE, a value constraint beyond type, and several
logical schemas are each expressible only via workaround. IE notation marks
several attributes with a repeated `*` marker and Chen notation marks
several attributes `<<key>>` or nests sub-attributes, but neither asserts a
single joint key; a 2021 community forum question asking exactly how to draw
a composite-key relation received no documented built-in answer. A real
`enum` keyword exists but declares a separate UML enumeration element rather
than constraining an attribute's value set. No CHECK-constraint or
multi-column UNIQUE keyword exists; only a free-text note can carry either.
The `namespace`/`package` keyword provides real dotted-qualified-name
scoping but has no declared connection to database-schema semantics. The
cross-cutting `domain_id` convention is not expressible anywhere in the
notation or the CLI.

PlantUML passes the plain-text/product-neutral MUST. It passes the validator
MUST for syntax errors, with the most explicit, primary-sourced exit-code
documentation found across all seven candidates: the legacy CLI exits -1 on
any diagram error, and the newer beta CLI documents 0 for success and 50,
100, or 200 for specific failure classes, alongside a `--check-syntax` flag
for validation without rendering. Semantic validation beyond syntax,
however, is not expressible: whether a relation referencing a previously
undeclared entity is silently auto-created — well known for PlantUML class
diagrams generally — or rejected was not confirmed against a primary source
specific to ER or IE diagrams. PlantUML passes the Docker MUST: official
`plantuml/plantuml` and `plantuml/plantuml-server` images are confirmed
current on Docker Hub, tied to the same release as the source, with `--svg`
and `--png` as documented, first-class flags.

PlantUML's licensing is multi-license rather than a single identifier:
GPL-3.0-or-later is the root default, with the same source additionally
offered, at the licensee's option, under five other licenses via dedicated
subprojects, per the project's own authoritative `LICENSES.md`. GitHub's own
repository-metadata auto-detection reports the SPDX field as `LGPL-3.0`,
which directly contradicts the actual root LICENSE file. Governance rests
with a single named copyright holder (Arnaud Roques, 2009–2026) with no
foundation or steering committee. PlantUML is not at risk of abandonment. It
has a real named-subset text-inclusion mechanism (`!startsub`/`!endsub`/
`!includesub`), but it operates on author-tagged line ranges rather than
model-aware entity selection. No application-type generation of any kind
exists, corroborated by both an exhaustive output-format table (all ten
formats are diagrams or markup, none application code) and a zero-hit
GitHub search for `pydantic` or `sqlalchemy`. DDL derivation is therefore
not applicable.

*Sources:* [source-plantuml-ie-notation.json](sources/source-plantuml-ie-notation.json),
[source-plantuml-ie-validation-exit.json](sources/source-plantuml-ie-validation-exit.json),
[source-plantuml-ie-generation.json](sources/source-plantuml-ie-generation.json),
[source-plantuml-ie-docker-registry.json](sources/source-plantuml-ie-docker-registry.json),
[source-plantuml-ie-licence-governance.json](sources/source-plantuml-ie-licence-governance.json),
[source-plantuml-ie-contrary-evidence.json](sources/source-plantuml-ie-contrary-evidence.json).

#### Prisma schema language

Composite primary keys, JSON payload columns, enumerated domains, multiple
self-referencing foreign keys, nullable foreign keys, multi-column UNIQUE,
and one-to-zero-or-one are all expressible in the Prisma Schema Reference.
`@@id([...])` covers composite keys for every provider except MongoDB, which
the documentation states explicitly does not support them. The native `Json`
scalar and the `enum` block are both documented, though neither is supported
on Microsoft SQL Server — a provider-conditional gap on top of the general
product-neutrality problem below. A value constraint beyond type is not
expressible: the Database Features Matrix states plainly that CHECK
constraints have no Prisma-schema representation, corroborated independently
by an open GitHub issue (prisma/prisma#3388, opened December 2019, still
open) stating outright that there is no way to express SQL CHECK constraints
in the schema. Several logical schemas are expressible only via workaround,
since the `multiSchema` feature is limited to PostgreSQL, CockroachDB, and
SQL Server. The cross-cutting `domain_id` convention is not expressible; no
lint or rule mechanism exists in any documented subcommand.

Prisma fails the product-neutrality half of the first MUST on a strict
reading: a `.prisma` file cannot be written without choosing exactly one
`provider` from a closed six-value enum, with no unset or generic option
documented anywhere, so authoring a valid schema is itself an act of picking
a database product. Its validator MUST is expressible only via workaround:
`prisma validate` and `prisma format --check` are documented to detect
errors with a distinct error code and count, and the latter is explicitly
framed for CI use, but neither page states a numeric exit-code contract
outright. Prisma fails the Docker MUST: no official Docker image exists (the
only plausibly named Docker Hub image, `prismagraphql/prisma`, is the
deprecated Prisma-1 GraphQL-server product, unmaintained since 2019); the
officially recommended path is a hand-built Dockerfile around a generic
Node base image. SVG and PNG are available only through the unofficial
third-party `prisma-erd-generator`, which itself depends on
`@mermaid-js/mermaid-cli` and Puppeteer.

Prisma is Apache-2.0 licensed under single-vendor, commercially-backed
governance (Prisma Data, Inc., with named venture-capital investors), with
no governance charter. A load-bearing nuance: the actively-committed default
branch is a documented pre-1.0 rewrite ("Prisma Next"), while the
production-recommended version lives on a separate branch. Prisma is not at
risk of abandonment. No first-party named-subset-view mechanism exists;
Python application-type generation exists only through the third-party
`prisma-client-py`, which GitHub's own archived flag and the project's own
README confirm is no longer maintained. DDL derivation is first-party and
real through `prisma migrate diff --script`, provider-bound and only
partially supported for MongoDB.

*Sources:* [source-prisma-schema-reference.json](sources/source-prisma-schema-reference.json),
[source-prisma-product-neutrality.json](sources/source-prisma-product-neutrality.json),
[source-prisma-tooling.json](sources/source-prisma-tooling.json),
[source-prisma-docker-registry.json](sources/source-prisma-docker-registry.json),
[source-prisma-licence-governance.json](sources/source-prisma-licence-governance.json),
[source-prisma-generation.json](sources/source-prisma-generation.json).

#### Atlas HCL (ariga.io)

Composite primary keys, multiple self-referencing foreign keys, nullable
foreign keys, multi-column UNIQUE, and several logical schemas in one
database are all expressible in the Atlas HCL language reference. JSON
payload columns are expressible only via workaround, since the exact type
name is dialect-specific. Enumerated domains are expressible but not as one
construct: MySQL uses an inline `enum` type while PostgreSQL requires a
separately declared top-level `enum` schema object, and one closed issue
shows PostgreSQL enum value reordering is explicitly unsupported by the
migration flow once created. One-to-zero-or-one and a value constraint
beyond type are expressible only via workaround, the former reconstructed
from a nullable foreign key plus a unique index, the latter written as raw,
dialect-specific SQL text inside a `check` block. The several-logical-
schemas construct, while documented and directly matching Gigacron's
configuration/runtime/audit/resources split, is complicated by two open
GitHub issues: one where a multi-schema `apply` silently reports no changes
despite a genuine diff, and one where same-named tables across schema files
collide unless every table uses the qualified naming form. The cross-cutting
`domain_id` convention is expressible only via workaround: Atlas ships a
purpose-built Schema Rule language for exactly this class of policy, but it
is licensed exclusively to Pro and Enterprise accounts.

Atlas's product-neutrality is only partially satisfied: structural HCL
keywords are dialect-neutral, but column type names, the enum declaration
shape, and CHECK expression syntax all diverge per dialect, and semantic
validation requires a live "dev database," which Atlas can spin up as an
ephemeral Docker container but which commits the validator's own runtime to
one specific database engine and version. Its validator MUST is expressible
only via workaround: `atlas schema validate` is documented only in prose
("returns an error"), and the sole primary-source passage with an explicit
numeric exit code is scoped to `atlas migrate lint`'s destructive-change
analyzer, not to `schema validate` or `schema lint` by name. Atlas fails the
Docker MUST for the visualization capability specifically: the official
`arigaio/atlas` image is confirmed current and actively published, but every
documented description of Atlas's ERD capability routes through Atlas Cloud
rather than a local file export. DDL derivation from the same image, by
contrast, is a genuine local, container-runnable capability.

Atlas has a three-tier licensing structure: an Apache-2.0 "Community
Edition"; a free-but-proprietary "Atlas MSA" standard distribution most
users actually run, with additional proprietary features and a wider
database-driver list; and a further paid Atlas Pro/Enterprise tier. Two
official Ariga pages directly contradict each other on whether Schema
Visualization requires that paid tier (one states Pro Plan Only, the other
lists it under the free Starter tier); this survey records the contradiction
rather than resolving it. No governance charter exists; Atlas is
single-vendor (Ariga, Inc.). It is not at risk of abandonment, though an
unresolved discrepancy exists between two Atlas source records over a Docker
tag apparently one day ahead of the latest tag the GitHub API itself
reports. No named or reusable view construct exists; application-type
generation exists only in the reverse direction (importing SQLAlchemy models
to extract an Atlas schema); DDL derivation is a genuine, first-party, strong
capability.

*Sources:* [source-atlas-hcl-hcl-language.json](sources/source-atlas-hcl-hcl-language.json),
[source-atlas-hcl-product-neutrality.json](sources/source-atlas-hcl-product-neutrality.json),
[source-atlas-hcl-validation-exit.json](sources/source-atlas-hcl-validation-exit.json),
[source-atlas-hcl-generation.json](sources/source-atlas-hcl-generation.json),
[source-atlas-hcl-docker-registry.json](sources/source-atlas-hcl-docker-registry.json),
[source-atlas-hcl-licence-governance.json](sources/source-atlas-hcl-licence-governance.json),
[source-atlas-hcl-contrary-evidence.json](sources/source-atlas-hcl-contrary-evidence.json).

#### D2 with SQL table shapes

Of the ten constructs, only three are expressible in any form, and none is
fully expressible without a workaround. Multiple self-referencing foreign
keys, one-to-zero-or-one, and several logical schemas are each expressible
only via workaround: connections can link a table to itself with no FK-
specific semantics attached; crow's-foot-style arrowheads are a purely
visual styling choice the compiler does not interpret as a cardinality
constraint; and D2's generic `container` primitive can visually nest tables
into groups resembling schemas, but the documentation attaches no schema-
specific semantics to it. JSON payload columns are expressible only as an
uninterpreted free-text label. Composite primary keys, enumerated domains,
nullable foreign keys, multi-column UNIQUE, a value constraint beyond type,
and the cross-cutting `domain_id` convention are all not expressible.
Composite primary keys are the one construct in this entire survey confirmed
not expressible by an explicit, first-party maintainer statement rather
than by absence of mention: a still-open GitHub feature request
(d2lang/d2#671, opened 2023-01-16) states plainly, "At the moment d2 can't
represent FKs that are composed of more than one column," with the
reporter's own example showing no available syntax for a joint key. The
documented `constraint: [primary_key; unique]` array syntax applies multiple
constraint labels to one column; it does not let two columns jointly form
one constraint, a distinction easy to mistake for composite-key support.

D2 passes the plain-text/product-neutral MUST, though this neutrality
follows largely from the shape enforcing almost no real semantics rather
than genuine dialect abstraction. D2 has the best source-confirmed answer to
the validator MUST of all seven candidates: direct reading of
`d2cli/validate.go` and the shared `xmain.go` library shows any validation
error propagates to a handler that calls `os.Exit(code)`, defaulting to 1.
However, `validate` calls only the syntax parser, never the semantic
compiler used by the render path, and D2 has no "undeclared shape" error
class at all by design, since connection syntax auto-declares any shape it
references — so the specific semantic test case this survey probed for is
moot for D2, not merely uncaught. D2's Docker MUST is open: the official
image is current, and SVG export is native and dependency-free, but PNG
depends on Playwright launching a headless Chromium brow­ser, and whether
the official image bundles that dependency pre-installed or downloads it on
first use was not confirmed by any source consulted.

D2 itself is licensed under the Mozilla Public License 2.0, distinct from
the optional, proprietary, closed-source TALA layout engine, which the
project's own documentation states plainly is "Not free." D2 functions
fully without TALA, since the open-source ELK layout engine provides the
same row-level foreign-key routing accuracy documented as a TALA benefit.
No governance charter exists; D2 is single-vendor (Terrastruct Inc., which
also sells TALA). D2's most recent commit is well within the freshness
window, though its most recent tagged release is a full year older — the
widest release-versus-activity gap found among the seven candidates,
though not enough on its own to trigger the brief's abandonment flag.
`Layers`, `Scenarios`, and `Steps` produce multiple named boards from one
source file, but their documented purpose is overlay and abstraction-level,
not subset selection over an existing large model. No application-type
generation of any kind exists, and DDL derivation is therefore not
applicable.

*Sources:* [source-d2-sql-table-sql-table-shape.json](sources/source-d2-sql-table-sql-table-shape.json),
[source-d2-sql-table-validation-exit.json](sources/source-d2-sql-table-validation-exit.json),
[source-d2-sql-table-generation.json](sources/source-d2-sql-table-generation.json),
[source-d2-sql-table-docker-registry.json](sources/source-d2-sql-table-docker-registry.json),
[source-d2-sql-table-licence-governance.json](sources/source-d2-sql-table-licence-governance.json),
[source-d2-sql-table-contrary-evidence.json](sources/source-d2-sql-table-contrary-evidence.json).

### Language expressiveness and toolchain maturity move independently

The recorded evidence shows expressiveness and tooling maturity are not
correlated, and cut in opposite directions for different candidates. Atlas
HCL combines a rich language with a real Docker-published validator, yet its
ERD visualization is cloud-only and the custom schema-rule engine needed for
the `domain_id` convention is paid. LinkML combines the richest construct
coverage of any YAML-based candidate with the only two first-party
generators (Pydantic and SQLAlchemy) found in this survey, yet its diagram
generator cannot produce SVG or PNG at all. DBML combines a rich language,
including a genuine named-view construct, with a CLI whose own source code
never sets a non-zero exit code and no official Docker image anywhere.
Mermaid combines a thin language — no composite keys, no enums, no schemas,
no cross-cutting rules — with the most mature, actively-published Docker
tooling in the survey, but zero semantic validation, so mature tooling sits
on top of a language that cannot express or check what Gigacron needs.
PlantUML combines a moderate, workaround-heavy language with the most
explicit, primary-sourced numeric exit-code contract found in this survey
and solid native Docker SVG and PNG, but zero application-type generation of
any kind. Prisma combines strong construct coverage for most constructs with
a completely absent official Docker image and an archived, self-declared
unmaintained third-party Python generator. D2 combines almost no real
relational semantics in its `sql_table` shape with the most rigorously
source-confirmed non-zero-exit validator behaviour in the survey and
dependency-free native SVG export. On the evidence gathered, no candidate
combines strong construct expressiveness, a confirmed CI-gatable validator,
and confirmed zero-local-install SVG-plus-PNG rendering all at once.

*Sources:* [source-dbml-tooling.json](sources/source-dbml-tooling.json),
[source-dbml-docker-registry.json](sources/source-dbml-docker-registry.json),
[source-dbml-grammar.json](sources/source-dbml-grammar.json),
[source-mermaid-erd-tooling.json](sources/source-mermaid-erd-tooling.json),
[source-mermaid-erd-docker-registry.json](sources/source-mermaid-erd-docker-registry.json),
[source-mermaid-erd-grammar.json](sources/source-mermaid-erd-grammar.json),
[source-linkml-tooling.json](sources/source-linkml-tooling.json),
[source-linkml-generation.json](sources/source-linkml-generation.json),
[source-plantuml-ie-validation-exit.json](sources/source-plantuml-ie-validation-exit.json),
[source-plantuml-ie-generation.json](sources/source-plantuml-ie-generation.json),
[source-prisma-docker-registry.json](sources/source-prisma-docker-registry.json),
[source-prisma-generation.json](sources/source-prisma-generation.json),
[source-atlas-hcl-generation.json](sources/source-atlas-hcl-generation.json),
[source-atlas-hcl-licence-governance.json](sources/source-atlas-hcl-licence-governance.json),
[source-d2-sql-table-validation-exit.json](sources/source-d2-sql-table-validation-exit.json),
[source-d2-sql-table-sql-table-shape.json](sources/source-d2-sql-table-sql-table-shape.json).

### MUST-criteria pass/fail matrix

The brief sets three MUSTs: the model source must be a plain-text,
version-controlled, product-neutral source of truth; a validator must exit
non-zero on a malformed or internally inconsistent model; and the toolchain
must render SVG and PNG from an ephemeral Docker container with no local
install.

| Candidate         | Plain-text / product-neutral                       | Validator exits non-zero                                             | SVG + PNG, ephemeral Docker                             |
| ----------------- | -------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------- |
| DBML              | Pass                                               | Fail                                                                 | Fail                                                    |
| Mermaid erDiagram | Pass                                               | Fail                                                                 | Pass                                                    |
| LinkML            | Pass                                               | Partial (pass via `linkml-lint`; `validate`'s contract undocumented) | Fail                                                    |
| PlantUML IE/Chen  | Pass                                               | Partial (pass for syntax; semantic check unconfirmed)                | Pass                                                    |
| Prisma            | Fail (provider is mandatory)                       | Partial (documented failure behaviour, no stated exit code)          | Fail                                                    |
| Atlas HCL         | Partial (dialect leak at type/check/runtime level) | Partial (exit code confirmed only for `migrate lint`)                | Fail (viz is cloud-only; DDL derivation passes locally) |
| D2                | Pass                                               | Pass (syntax; semantic check moot by design)                         | Partial (SVG confirmed; PNG dependency unconfirmed)     |

On this evidence, no surveyed candidate passes all three MUSTs cleanly.

*Sources:* [source-dbml-tooling.json](sources/source-dbml-tooling.json),
[source-dbml-docker-registry.json](sources/source-dbml-docker-registry.json),
[source-mermaid-erd-tooling.json](sources/source-mermaid-erd-tooling.json),
[source-mermaid-erd-docker-registry.json](sources/source-mermaid-erd-docker-registry.json),
[source-mermaid-erd-grammar.json](sources/source-mermaid-erd-grammar.json),
[source-linkml-tooling.json](sources/source-linkml-tooling.json),
[source-linkml-docker-registry.json](sources/source-linkml-docker-registry.json),
[source-plantuml-ie-validation-exit.json](sources/source-plantuml-ie-validation-exit.json),
[source-plantuml-ie-docker-registry.json](sources/source-plantuml-ie-docker-registry.json),
[source-prisma-tooling.json](sources/source-prisma-tooling.json),
[source-prisma-docker-registry.json](sources/source-prisma-docker-registry.json),
[source-prisma-product-neutrality.json](sources/source-prisma-product-neutrality.json),
[source-atlas-hcl-validation-exit.json](sources/source-atlas-hcl-validation-exit.json),
[source-atlas-hcl-generation.json](sources/source-atlas-hcl-generation.json),
[source-atlas-hcl-product-neutrality.json](sources/source-atlas-hcl-product-neutrality.json),
[source-d2-sql-table-validation-exit.json](sources/source-d2-sql-table-validation-exit.json),
[source-d2-sql-table-docker-registry.json](sources/source-d2-sql-table-docker-registry.json).

### Licence and governance: free-core/paid-tier splits and one metadata contradiction

Atlas HCL has a three-tier licensing structure: an Apache-2.0 "Community
Edition," a free-but-proprietary "Atlas MSA" standard distribution, and a
paid Pro/Enterprise tier. The custom Schema Rule language needed for the
`domain_id` convention is confirmed Pro/Enterprise-only by two non-
conflicting official pages, and ERD visualization's tier status is the
subject of a direct, unresolved contradiction between two official Ariga
pages.

PlantUML shows the one confirmed case in this survey of repository metadata
disagreeing with the actual LICENSE file: GitHub's auto-detected SPDX field
reports "LGPL-3.0," which directly contradicts the actual root LICENSE file
(full GPL-3.0-or-later text) and the project's own authoritative
`LICENSES.md`.

D2 has an MPL-2.0 open core plus an optional, explicitly "Not free"
proprietary layout engine (TALA) that is not required for any MUST-relevant
capability, since the open-source ELK engine provides the same row-level
foreign-key routing accuracy.

Prisma is fully Apache-2.0, but under single-vendor, commercially-backed
governance with no foundation, and with a documented nuance where the
actively-committed default branch is a pre-1.0 rewrite while the
production-recommended version lives on a separate branch.

DBML, Mermaid, and LinkML are each fully open (Apache-2.0, MIT, and
Apache-2.0 respectively) with no paid tier found, and each lacking a formal
governance charter, resting on single-vendor maintainer-led (DBML) or
informal (Mermaid, LinkML) patterns.

*Sources:* [source-atlas-hcl-licence-governance.json](sources/source-atlas-hcl-licence-governance.json),
[source-atlas-hcl-validation-exit.json](sources/source-atlas-hcl-validation-exit.json),
[source-plantuml-ie-licence-governance.json](sources/source-plantuml-ie-licence-governance.json),
[source-d2-sql-table-licence-governance.json](sources/source-d2-sql-table-licence-governance.json),
[source-prisma-licence-governance.json](sources/source-prisma-licence-governance.json),
[source-dbml-licence-governance.json](sources/source-dbml-licence-governance.json),
[source-mermaid-erd-licence-governance.json](sources/source-mermaid-erd-licence-governance.json),
[source-linkml-licence-governance.json](sources/source-linkml-licence-governance.json).

### Named subset views, application-type generation, and DDL derivation

DBML's `DiagramView` construct is the only genuinely model-aware, named-view
language construct found in the survey, though whether any open-source
renderer honours it is unconfirmed. D2's Layers/Scenarios/Steps and
PlantUML's `!includesub` are real but workaround-level. Atlas offers only ad
hoc flag re-runs, not a saved artefact. LinkML's subset tagging is not
documented as connected to diagram generation. Mermaid and Prisma have no
first-party mechanism at all.

LinkML is the only candidate with two first-party application-type
generators (Pydantic and SQLAlchemy) plus a separate SQL DDL generator, the
broadest generation surface in the survey, but construct survival through
generation is uneven. DBML, PlantUML, D2, and Atlas have no first-party
application-type generator at all; DBML and Prisma each have an unofficial
third-party option, the latter explicitly self-declared no longer
maintained.

DDL derivation is strong and first-party for Atlas, DBML, and Prisma; it
shares LinkML's construct-survival gaps for LinkML; it is not applicable for
PlantUML and D2, since neither has a generation pipeline to derive it from;
and Mermaid has no generation of any kind.

*Sources:* [source-dbml-grammar.json](sources/source-dbml-grammar.json),
[source-dbml-generation.json](sources/source-dbml-generation.json),
[source-atlas-hcl-generation.json](sources/source-atlas-hcl-generation.json),
[source-linkml-generation.json](sources/source-linkml-generation.json),
[source-linkml-metamodel.json](sources/source-linkml-metamodel.json),
[source-plantuml-ie-notation.json](sources/source-plantuml-ie-notation.json),
[source-plantuml-ie-generation.json](sources/source-plantuml-ie-generation.json),
[source-d2-sql-table-generation.json](sources/source-d2-sql-table-generation.json),
[source-d2-sql-table-contrary-evidence.json](sources/source-d2-sql-table-contrary-evidence.json),
[source-prisma-generation.json](sources/source-prisma-generation.json),
[source-prisma-schema-reference.json](sources/source-prisma-schema-reference.json),
[source-mermaid-erd-grammar.json](sources/source-mermaid-erd-grammar.json),
[source-mermaid-erd-syntax.json](sources/source-mermaid-erd-syntax.json).

### Release and repository activity

All seven candidates show either a tagged release or repository activity
within the eighteen months before August 2026. DBML released near-daily
through August 2026. Mermaid's core was pushed the same day as retrieval.
LinkML released roughly three months before retrieval. PlantUML released in
June 2026 with a push in August. Prisma committed the same day as retrieval,
with the caveat that part of that activity sits on a pre-1.0 rewrite branch.
Atlas released in early August 2026, with an unresolved cross-record
discrepancy over a Docker tag apparently one day ahead of the latest tag the
GitHub API itself reports. D2 is the one candidate where release recency and
activity recency diverge widely: its most recent commit is four days before
retrieval, but its most recent tagged release is a full year older. None of
the seven candidates is flagged at risk of abandonment under the brief's
freshness requirements.

*Sources:* [source-dbml-licence-governance.json](sources/source-dbml-licence-governance.json),
[source-mermaid-erd-licence-governance.json](sources/source-mermaid-erd-licence-governance.json),
[source-mermaid-erd-tooling.json](sources/source-mermaid-erd-tooling.json),
[source-linkml-licence-governance.json](sources/source-linkml-licence-governance.json),
[source-plantuml-ie-licence-governance.json](sources/source-plantuml-ie-licence-governance.json),
[source-prisma-licence-governance.json](sources/source-prisma-licence-governance.json),
[source-atlas-hcl-licence-governance.json](sources/source-atlas-hcl-licence-governance.json),
[source-atlas-hcl-docker-registry.json](sources/source-atlas-hcl-docker-registry.json),
[source-d2-sql-table-licence-governance.json](sources/source-d2-sql-table-licence-governance.json),
[source-d2-sql-table-docker-registry.json](sources/source-d2-sql-table-docker-registry.json).

## Uncertainties

- Atlas HCL: two official Ariga pages directly contradict each other on
  whether Schema Visualization is Pro-plan-only or included in the free
  Starter tier. Neither page is dated, and no third page arbitrates. This
  report records the contradiction without resolving it.
- PlantUML: GitHub's own auto-detected SPDX licence field ("LGPL-3.0")
  contradicts the actual root LICENSE file (full GPL-3.0-or-later text) and
  the project's own authoritative `LICENSES.md`. This report treats
  `LICENSES.md` as authoritative, but the contradiction itself remains
  unresolved in the source base.
- Atlas HCL: a Docker Hub tag apparently pushed one day ahead of the latest
  tag reported by the GitHub Releases and Tags API is an unresolved
  discrepancy between two Atlas source records.
- Several "expressible" verdicts for multi-attribute constructs (composite
  primary keys and multi-column indexes for Atlas HCL; three simultaneous
  self-referencing foreign keys for both DBML and Atlas HCL) are extrapolated
  from a general grammar rule or a smaller worked example, not from a
  literal example matching Gigacron's exact cardinality.
- Whether PlantUML's well-known class-diagram behaviour of auto-creating an
  empty entity for an undeclared reference also applies, unmodified, to its
  ER/IE notation specifically was not confirmed against a primary source
  dedicated to ER/IE diagrams.
- D2: whether the official Docker image bundles Playwright and Chromium
  pre-installed for PNG export, or downloads them on first invocation, was
  not confirmed by any source consulted.
- DBML: whether any open-source SVG renderer honours the documented
  `DiagramView` filter when producing an image was not confirmed.

## Evidence gaps

- Atlas HCL: the `domain_id` cross-cutting convention and the
  one-to-zero-or-one relationship were never queried against the GitHub
  issue tracker at all, because no plausible search vocabulary was
  identified for either. This is an unexecuted search, explicitly distinct
  from a search that ran and found nothing.
- LinkML's contrary-evidence search used the general web-search tool rather
  than the authenticated GitHub Issues API; the LinkML source record itself
  flags this as a weaker method than the API-based approach used for Atlas,
  DBML, and part of Prisma's searches. LinkML's "not found" results
  therefore carry less weight than those API-based searches.
- LinkML's SQL DDL generator's enum-rendering mechanism (a native CHECK
  constraint versus a separate lookup table) was not confirmed by any
  fetched generator documentation page.
- LinkML's `unique_keys` to SQL UNIQUE constraint emission by the SQL DDL
  generator was not confirmed by any fetched generator documentation page.
- DBML: three specific DDL-derivation claims — self-referencing foreign key,
  multi-column UNIQUE, and one-to-one-with-uniqueness — were not found
  demonstrated in any examined golden-file exporter-test fixture.
- Prisma: no documented hard limit on the number of named self-relations a
  single model may declare was found; absence of a stated limit is not
  proof no limit exists.
- Prisma: construct-by-construct DDL fidelity through `prisma migrate diff --script`, beyond the CHECK-constraint gap already known to be absent
  upstream in the schema, was not independently tested.
- D2 and Atlas HCL: neither project's GHCR mirror, if any exists, was
  exhaustively confirmed; Docker Hub alone was sufficient to answer the
  availability question for both.

## Limitations

- No candidate was installed, executed, or rendered as part of this survey.
  Every capability, exit-code, and generation-fidelity finding in this
  report rests on documentary evidence — official documentation, source-code
  reading, golden-file test fixtures, and public registry-API listings — not
  on an observed process run.
- The mandatory contrary-evidence search was executed with materially
  different rigor across candidates. Atlas HCL's, DBML's, and part of
  Prisma's searches queried the GitHub Search API directly, an authoritative
  and reproducible method. LinkML's own contrary-evidence record explicitly
  flags that it used a general web-search tool instead and recommends the
  API-based method as a stronger follow-up.
- Several Mermaid source records internally cite a
  `source-mermaid-erd-contrary-evidence.json` record — for example, two
  specific GitHub issue numbers and a predecessor-repository issue — that
  does not exist in `docs/research/data-modeling-dsl/sources/`, confirmed by
  direct directory listing. This report does not cite that non-existent
  file and does not treat those specific issue numbers as independently
  verified evidence; the underlying claims are instead corroborated here
  only through the grammar and source-code readings in the Mermaid grammar
  and tooling records.
- Atlas HCL's licence-governance and contrary-evidence source records were
  produced by a separate backfill research dispatch after a session
  interruption, per the instructions given to this synthesis. This report
  checked their content for internal consistency with the other five Atlas
  HCL facet records but did not independently verify the backfill dispatch's
  own provenance.
- Freshness and activity dates reflect each source record's own retrieval
  date, predominantly 2026-08-14, and will drift from the date of any future
  re-reading of this report.
- Several source records substitute their own retrieval date for a genuine
  page "last-updated" date where the underlying documentation carried no
  visible revision date; this affects the precision, not the substance, of
  the findings drawn from them.
- Docker registry queries in several records retrieved only the first page
  of tags rather than the full historical inventory; this is sufficient to
  establish current availability and freshness but not a complete version
  history.

## Candidates for deeper falsification study

- **DBML** — run `@dbml/cli`'s `dbml2sql` against a schema modeled on
  Gigacron's actual composite keys, self-referencing foreign keys,
  multi-column UNIQUE, and one-to-one relationships, and inspect whether the
  generated DDL preserves each construct as the golden-file fixtures suggest
  but do not directly confirm; also confirm whether the open-source
  `dbml-renderer` honours the documented `DiagramView` construct, and
  whether a wrapper script can reliably produce a non-zero CI exit code.
- **Atlas HCL** — author Gigacron's four-schema split in Atlas HCL and run
  `atlas schema apply --dry-run` against a real ephemeral Docker dev
  database to see whether the several-logical-schemas mechanism applies
  cleanly given the two open GitHub issues describing silent no-ops and
  table-name collisions; also confirm exactly which capabilities remain
  available at the free tier versus require a paid login, given the direct
  contradiction found on ERD visualization gating.
- **LinkML** — run `gen-sqlddl` and the Pydantic and SQLAlchemy generators
  against a schema modeling Gigacron's composite identity, JSON payload
  columns, and the `resource_task_weight` value constraint, to determine
  whether these constructs actually survive generation as this survey's
  documentary evidence suggests they do not, or whether the documentation is
  simply incomplete on this point.
- **PlantUML IE/Chen** — feed a diagram referencing an undeclared entity into
  both command-line interfaces to confirm, at last, whether PlantUML
  auto-creates an empty box or rejects it for ER/IE diagrams specifically,
  since no primary source for this behaviour was found despite it being the
  single most consequential unresolved question for PlantUML's viability as
  a CI-gate validator.
- **Prisma** — run `prisma validate` and `prisma format --check` against a
  deliberately malformed schema to observe the actual exit code, never
  confirmed as an explicit numeric contract in the documentation, and run
  `prisma migrate diff --script` against a schema containing Gigacron's
  advanced constructs to see which actually survive into derived DDL.
- **D2** — run `d2 validate` and a full render against a Gigacron-shaped
  `sql_table` model to confirm the documented exit-on-error behaviour in
  practice, and pull the official Docker image and attempt a PNG export with
  no prior local Playwright installation, to settle whether the image
  bundles Chromium or triggers an on-the-fly download that would break a
  zero-local-install CI gate.
- **Mermaid erDiagram (incumbent baseline)** — feed `mmdc` a diagram with a
  relationship referencing an undeclared entity to confirm, by direct
  observation, that it renders successfully with exit code 0 rather than
  failing — the single most consequential finding this survey uncovered
  against the incumbent, currently resting on source-code reading rather
  than an observed process exit.
