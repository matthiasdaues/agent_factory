# Research Survey Plan — Knowledge Graph State Of The Art

The plan follows [research-brief.json](research-brief.json). It splits the survey by the six scope areas of the brief, so no two assignments research the same concept. All six assignments run in parallel as one wave.

## Research Questions

1. Area 1: What data models do knowledge graphs use, and what is the 2026 standards status of RDF 1.2, SPARQL 1.2, ISO GQL, and SQL/PGQ?
2. Area 2: How do knowledge graphs make statements about statements, and how did reification, named graphs, RDF-star, and the Wikidata statement model replace or criticize each other?
3. Area 3: How do PROV-O, nanopublications, micropublications, and argumentation models record provenance and claims?
4. Area 4: How do OWL open-world reasoning, SHACL, and ShEx differ in validating graph data?
5. Area 5: How do temporal and bitemporal graphs, entity resolution, and owl:sameAs handle time and identity?
6. Area 6: How do language models build and use knowledge graphs, and what do GraphRAG, agent memory graphs, and embedded stores document?
7. Across areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?

## Search Angles

- W3C and ISO pages for specification status, drafts, and change logs
- The original paper or specification for each concept, then the papers that criticized it
- W3C community group reports, working group issue trackers, and mailing list threads that record criticism
- Peer-reviewed surveys, starting with Hogan et al., Knowledge Graphs, ACM Computing Surveys 2021
- Project documentation for Wikidata, PROV, nanopublications, SHACL, and ShEx
- Papers from 2023 onward on LLM-based extraction, GraphRAG, and agent memory graphs
- Position papers and critiques, such as those on owl:sameAs misuse and open-world assumptions

## Source Targets

- w3.org specifications, working drafts, and group pages for RDF 1.2, SPARQL 1.2, SHACL, and PROV-O
- iso.org catalogue pages for ISO/IEC 39075 (GQL) and ISO/IEC 9075-16 (SQL/PGQ)
- Original papers on reification, singleton properties, RDF-star, and Wikidata's data model
- Nanopublication, micropublication, and Argument Interchange Format papers and documentation
- ShEx specification and SHACL-versus-ShEx comparison papers
- Papers on temporal and bitemporal graph models, entity resolution, and owl:sameAs studies
- ACL, arXiv, and venue papers on GraphRAG and agent memory graphs, from 2023 onward
- Project documentation for embedded or file-based graph stores, used only for stated features

## Assignments

Each assignment declares agent, tier, independent session, a unique output path, and a bounded task. Every task includes the history requirement: for each hardened concept in its area, record the sequence of formulations and the criticism that drove each change, with one source per step. Area 1 alone owns the standards status. Area 2 covers the concept history of RDF-star and triple terms.

| ID  | Agent      | Tier     | Area                                      | Output                                              | Independent Session |
| --- | ---------- | -------- | ----------------------------------------- | --------------------------------------------------- | ------------------- |
| A1  | researcher | standard | data models                               | sources/area-1-data-models.md                       | false               |
| A2  | researcher | standard | statements about statements               | sources/area-2-statements-about-statements.md       | false               |
| A3  | researcher | standard | provenance and claims                     | sources/area-3-provenance-and-claims.md             | false               |
| A4  | researcher | standard | validation and world assumptions          | sources/area-4-validation-and-world-assumptions.md  | false               |
| A5  | researcher | standard | time and identity                         | sources/area-5-time-and-identity.md                 | false               |
| A6  | researcher | standard | construction and use with language models | sources/area-6-construction-with-language-models.md | false               |

## Stop Conditions

- Each of the six scope areas has recorded sources for its main concepts.
- At least five concepts have a recorded sequence of formulations with the criticism and a source for each step.
- The status of RDF 1.2, SPARQL 1.2, ISO GQL, and SQL/PGQ is recorded from the pages of W3C and ISO.
- A secondary source is marked as secondary and used only where no primary source is reachable.
- No further sources are likely to change the findings materially.

## Structured Block

The block below is the plan in the shape of `research-survey-plan.schema.json`. The tasks in `assignments` are the full text each researcher receives.

```json
{
  "research_questions": [
    "Area 1: What data models do knowledge graphs use, and what is the 2026 standards status of RDF 1.2, SPARQL 1.2, ISO GQL, and SQL/PGQ?",
    "Area 2: How do knowledge graphs make statements about statements, and how did reification, named graphs, RDF-star, and the Wikidata statement model replace or criticize each other?",
    "Area 3: How do PROV-O, nanopublications, micropublications, and argumentation models record provenance and claims?",
    "Area 4: How do OWL open-world reasoning, SHACL, and ShEx differ in validating graph data?",
    "Area 5: How do temporal and bitemporal graphs, entity resolution, and owl:sameAs handle time and identity?",
    "Area 6: How do language models build and use knowledge graphs, and what do GraphRAG, agent memory graphs, and embedded stores document?",
    "Across areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?"
  ],
  "search_angles": [
    "W3C and ISO pages for specification status, drafts, and change logs",
    "The original paper or specification for each concept, then the papers that criticized it",
    "W3C community group reports, working group issue trackers, and mailing list threads that record criticism",
    "Peer-reviewed surveys, starting with Hogan et al., Knowledge Graphs, ACM Computing Surveys 2021",
    "Project documentation for Wikidata, PROV, nanopublications, SHACL, and ShEx",
    "Papers from 2023 onward on LLM-based extraction, GraphRAG, and agent memory graphs",
    "Position papers and critiques, such as those on owl:sameAs misuse and open-world assumptions"
  ],
  "source_targets": [
    "w3.org specifications, working drafts, and group pages for RDF 1.2, SPARQL 1.2, SHACL, and PROV-O",
    "iso.org catalogue pages for ISO/IEC 39075 (GQL) and ISO/IEC 9075-16 (SQL/PGQ)",
    "Original papers on reification, singleton properties, RDF-star, and Wikidata's data model",
    "Nanopublication, micropublication, and Argument Interchange Format papers and documentation",
    "ShEx specification and SHACL-versus-ShEx comparison papers",
    "Papers on temporal and bitemporal graph models, entity resolution, and owl:sameAs studies",
    "ACL, arXiv, and venue papers on GraphRAG and agent memory graphs, from 2023 onward",
    "Project documentation for embedded or file-based graph stores, used only for stated features"
  ],
  "assignments": [
    "A1 | agent: researcher | tier: standard | independent_session: false | area: data models | output: sources/area-1-data-models.md | task: Data models: RDF and OWL, labeled property graphs, and hybrids. Own the current standards status of W3C RDF 1.2, W3C SPARQL 1.2, ISO GQL, and SQL/PGQ as of 2026, taken from the pages of W3C and ISO. Report only the status of RDF-star and triple terms here; area 2 owns their concept history. For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with one source per step. Mark each source primary or secondary. State for each source what it shows and what it does not show.",
    "A2 | agent: researcher | tier: standard | independent_session: false | area: statements about statements | output: sources/area-2-statements-about-statements.md | task: Statements about statements: reification, n-ary relations, named graphs, singleton properties, RDF-star and RDF 1.2 triple terms, edge properties, and the Wikidata statement model with qualifiers, references, and ranks. Do not research standards status; area 1 owns it. For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with one source per step. Mark each source primary or secondary. State for each source what it shows and what it does not show.",
    "A3 | agent: researcher | tier: standard | independent_session: false | area: provenance and claims | output: sources/area-3-provenance-and-claims.md | task: Provenance and claims: W3C PROV-O, nanopublications, micropublications, and argumentation models such as the Argument Interchange Format. For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with one source per step. Mark each source primary or secondary. State for each source what it shows and what it does not show.",
    "A4 | agent: researcher | tier: standard | independent_session: false | area: validation and world assumptions | output: sources/area-4-validation-and-world-assumptions.md | task: Validation and world assumptions: OWL open-world reasoning, SHACL, and ShEx. For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with one source per step. Mark each source primary or secondary. State for each source what it shows and what it does not show.",
    "A5 | agent: researcher | tier: standard | independent_session: false | area: time and identity | output: sources/area-5-time-and-identity.md | task: Time and identity: temporal and bitemporal knowledge graphs, entity resolution, and the use and misuse of owl:sameAs. For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with one source per step. Mark each source primary or secondary. State for each source what it shows and what it does not show.",
    "A6 | agent: researcher | tier: standard | independent_session: false | area: construction and use with language models | output: sources/area-6-construction-with-language-models.md | task: Construction and use with language models: LLM-based extraction, GraphRAG and similar retrieval, agent memory graphs, and embedded or file-based stores. Use sources from 2023 onward. Exclude vendor marketing as evidence for capability or adoption. For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with one source per step. Mark each source primary or secondary. State for each source what it shows and what it does not show."
  ],
  "stop_conditions": [
    "Each of the six scope areas has recorded sources for its main concepts.",
    "At least five concepts have a recorded sequence of formulations with the criticism and a source for each step.",
    "The status of RDF 1.2, SPARQL 1.2, ISO GQL, and SQL/PGQ is recorded from the pages of W3C and ISO.",
    "A secondary source is marked as secondary and used only where no primary source is reachable.",
    "No further sources are likely to change the findings materially."
  ]
}
```
