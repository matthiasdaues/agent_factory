# External Methods And Tools: Knowledge Graph With Provenance

## Summary

Three approaches fit the factory: a typed IBIS-style idea record, PROV-style source links, and ADR/PEP-style status lifecycles. All three work as markdown files in git. The graph databases from the LLM era fit worst. They need a running store, and they decide nothing about do, won't do, or defer.

Checking status: "checked" means a fetch in this task returned the stated content. Fetches went through a summarizing tool, so wording is a paraphrase. Anything marked unchecked came from memory or a secondary source.

Factory constraints used for the fit judgment: markdown in git, deterministic gates, several CLIs, agents create and scripts validate (`README.md`, intro and "What is in the box"; `packages/factory/rulebooks/rules.md`, "Foundational principles"). Rules also forbid building more than the spec needs (YAGNI, same section).

## 1. Design rationale and argumentation models

**IBIS records questions and answers, not outcomes.** It has three node types. Issues are questions. Positions are possible answers. Arguments support or object to a position. Positions link only to issues, arguments only to positions. New issues can arise from existing ones. Checked: https://en.wikipedia.org/wiki/Issue-based_information_system. That page names gIBIS (graphical hypertext, late 1980s, Conklin) and Compendium (open-source graphical IBIS). It lists no decision states. IBIS has no built-in "decided" marker.

**QOC adds criteria.** Questions name design issues. Options answer them. Criteria compare options. An assessment links an option to a criterion as positive or negative. The authors call the analysis a coproduct of design, not a log of it. Checked via search summary, secondary sources: https://acawiki.org/Questions,_Options,_and_Criteria:_Elements_of_Design_Space_Analysis. The original paper (MacLean, Young, Bellotti, Moran, Human-Computer Interaction 6(3-4), 1991) was not read. Unchecked.

**DRL focuses on the decision.** Its elements are decision problems, alternatives, goals, claims, and groups. It extends the Potts and Bruns model (Lee and Lai, 1991). Checked via the same search, secondary sources only; the original is unchecked. Source disagreement on attribution noted there.

**Decision states.** None of the three defines do, won't do, or defer. They model the argument, not the verdict. The verdict needs a status field added on top.

**Fit.** IBIS maps cleanly to an idea-and-decision process: an idea is a position, a question is an issue, objections are arguments. The three types are few enough to validate with a script. The known cost, from the practice rather than a checked source: people tire of typing arguments. Unchecked.

## 2. Provenance standards

**PROV-O says "idea came from message" with one property.** Entity, Activity, and Agent are the core classes. A message and an idea are both entities. `prov:wasDerivedFrom` links idea to message. `prov:wasAttributedTo` names the author. Sub-properties refine the link: `wasQuotedFrom` (idea repeats part of the source), `hadPrimarySource` (source is the original), `wasRevisionOf` (idea restates an earlier idea). `wasInvalidatedBy` ends an entity's usability, which is close to "superseded". The qualification pattern records the activity that formed the idea. Checked: https://www.w3.org/TR/prov-o/ (first 100,000 of about 264,000 characters read; later parts, including qualified patterns, unchecked in full).

**Fit.** The vocabulary is small enough to borrow without adopting RDF. Three link types would cover most needs: derived-from (quote or paraphrase), attributed-to, and revision-of. Full PROV-O in Turtle would add a toolchain the factory does not have. Borrow the names, skip the triple store.

## 3. Personal and team knowledge practice

**Zettelkasten uses stable IDs and cross-references.** Luhmann gave each card a unique index number from a branching hierarchy. Notes carry tags and reference other notes. Checked: https://en.wikipedia.org/wiki/Zettelkasten. The article states no scaling limit.

**Evergreen notes add the principles.** Atomic (one idea per note), concept-oriented, densely linked, associative ontologies over hierarchies. The page names no scaling problem. It says the hard part is writing notes worth developing, and that the goal is insight, not capture. Checked: https://notes.andymatuschak.org/Evergreen_notes. A first fetch at https://andymatuschak.org/notes/ returned 404.

**Obsidian is markdown files plus links.** Wikilinks `[[Note]]`, heading links `#Heading`, and block links `#^id`. Renaming a file updates links. Block links work only in Obsidian. Checked: https://obsidian.md/help/links. The page did not discuss backlinks. A "files are plain markdown" claim is not on that page; unchecked.

**Logseq stores plain-text Markdown or org files locally.** Checked: https://en.wikipedia.org/wiki/Logseq. Block-level storage and any database version are not covered there. Unchecked.

**Roam and Tana: not checked.** The Tana article fetch returned 404. Roam was not fetched. From memory, both are outliners with block references and Tana uses typed "supertags". They keep data in a hosted store, not in plain files. Unchecked.

**What scales or breaks.** None of the checked sources report scaling data. A stated weakness, unchecked: link-only notes with no type say that two ideas relate, not how. That matters here, because do and won't do are relations to a decision, not to another idea.

**Fit.** Atomic notes with stable IDs and wikilink-style links fit best. Obsidian-style plain markdown also reads fine in any of the factory's CLIs. The apps themselves are optional.

## 4. Decision records

**ADRs keep the old record and mark it.** Nygard's original has Title, Context, Decision, Status, Consequences. Status is proposed, accepted, or deprecated/superseded, with a pointer to the replacement. Never reuse a number. Stored in the repository as `doc/arch/adr-NNN.md`. Checked: https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions.

**MADR adds options.** Sections: Context and Problem Statement, Decision Drivers, Considered Options, Decision Outcome (with Consequences), Pros and Cons of the Options. The `status` front-matter field is optional; its placeholder values are proposed, rejected, accepted, deprecated, and "superseded by ADR-XXXX". Checked: https://adr.github.io/madr/. MADR therefore covers "won't do" as `rejected` and "superseded" explicitly. It has no `deferred`.

**PEPs have the fullest state set.** Draft, Accepted, Provisional, Final, Deferred, Rejected, Withdrawn, Superseded, Active. Deferred means no progress. An editor may move a deferred PEP back to Draft. Rejected keeps the record. Withdrawn means the author gave up. PEPs are files in the `python/peps` repository, and git history is the record. Checked: https://peps.python.org/pep-0001/.

**Rust RFCs use the pull request as the state.** Merge means accepted and active. Closing the pull request means rejected. Completed RFCs leave the active list. The page lists whether to keep rejected RFCs as an open question, and it does not cover postponed RFCs. Checked: https://github.com/rust-lang/rfcs/blob/master/text/0002-rfc-process.md. This is the 2014 original; the current process may differ. Unchecked.

**Mapping to the stakeholder's states.**

| Stakeholder state | ADR / MADR    | PEP                 |
| ----------------- | ------------- | ------------------- |
| accept / do       | accepted      | Accepted, Final     |
| won't do          | rejected      | Rejected, Withdrawn |
| defer             | none          | Deferred            |
| superseded        | superseded by | Superseded          |

PEP is the only model that has all four. Its Withdrawn state (the author drops it) is a useful fifth: it differs from Rejected (a decider says no).

**Fit.** Best of the survey. These are already markdown files in git, with a status field a script can check. The factory writes ADRs already (skill `write-adr`, listed in the skill index; not re-read in this task).

## 5. LLM-era systems

**GraphRAG traces to source text.** Documents are chunked into TextUnits (default 1,200 tokens). An LLM extracts entities and relationships per unit. Hierarchical Leiden clustering builds communities, and the LLM writes community reports. "TextUnits are also referenced by extracted knowledge items, providing provenance back to the original source text." Checked: https://microsoft.github.io/graphrag/index/default_dataflow/. The repo says indexing "can be an expensive operation" and that the project is in maintenance mode, MIT license. Checked: https://github.com/microsoft/graphrag. Built for question answering over a corpus. It records no decisions.

**LightRAG links entities and relations to chunks and files.** Citation support was added in 2025.03. Defaults are in-memory with local file persistence, "suitable only for small-scale testing"; production uses PostgreSQL or similar. MIT license. Checked: https://github.com/HKUDS/LightRAG.

**Graphiti keeps raw input as episodes.** Episodes are "the ground truth stream", and derived entities and relationships link back to them. Facts have validity windows. A changed fact is invalidated, not deleted. Backends are Neo4j, FalkorDB, Amazon Neptune. Apache 2.0. Checked: https://github.com/getzep/graphiti. A second page confirms episodes and a bi-temporal model but does not explain how edges link to episodes. Checked: https://help.getzep.com/graphiti/getting-started/overview. The invalidate-not-delete pattern matches ADR supersession.

**Mem0 stores memories per user, session, and agent.** It does entity linking. The page does not mention source links. Apache 2.0. Checked: https://github.com/mem0ai/mem0. Weak on provenance.

**Cognee turns documents, code, and conversations into a graph.** Operations are remember, recall, improve, forget. External metadata is stamped on every chunk. The page describes no dedicated provenance system. Apache 2.0, with a licensed product for the production Postgres graph store. Checked: https://github.com/topoteretes/cognee.

**Idea extraction from meetings or chat with source links: no tool found.** I did not run a search for this tool class. That gap is open. Pipeline mechanics belong to Brief C.

**Fit.** These systems answer questions over a corpus. They do not model a decision lifecycle. Each needs a database or an LLM index at run time, which breaks "markdown in git" and the factory's rule that validation is deterministic (`packages/factory/rulebooks/rules.md`, "Foundational principles"). Two ideas transfer: Graphiti's episodes (keep the raw source immutable) and invalidate-not-delete. LLM extraction output is not reproducible, so a gate cannot check its content, only its shape and links.

## 6. Fit judgment

### Best fit

1. **ADR/PEP status lifecycle on atomic markdown records.** Use a PEP-like state set: proposed, accepted, rejected, deferred, withdrawn, superseded. A script can check the status value and that "superseded by" targets exist. The factory already writes ADRs in this style.
2. **IBIS-style typed records (issue, position, argument), with MADR's options and consequences as the decision shape.** Three types and a few link rules are checkable. QOC's criteria are optional and only needed where options are compared; the factory has a `pugh-matrix` skill for that (skill index).
3. **PROV-style source links, borrowed as three field names in front matter.** `derived-from`, `attributed-to`, `revision-of`. Source objects (a transcript, a message export) stay immutable, as in Graphiti's episodes. A gate checks that every link target exists.

Evergreen-note practice (one idea per file, stable ID, wikilinks) is the writing convention that carries all three.

### Worst fit

- **Graph databases and hosted indexes** (Neo4j, Graphiti, Cognee's Postgres graph, LightRAG production stores, Mem0 cloud). They live outside git, differ per CLI, and need a running service.
- **GraphRAG community reports.** They are large LLM summaries, which is what the practitioner avoids, and cost is high.
- **Hosted outliners** (Roam, Tana; unchecked). Data sits outside the repository.
- **Full PROV-O in RDF.** More toolchain than the problem needs.

## Open questions

- No tool that extracts ideas from meetings or chat with source links was searched for or found.
- Roam and Tana were not checked. Logseq block storage was not checked.
- MacLean (QOC) and Lee and Lai (DRL) originals were not read. Secondary sources only.
- Current Rust RFC process was not checked; only the 2014 text.
- Scaling limits of Zettelkasten, evergreen, and Obsidian practice have no checked source.
- Whether IBIS-style typing is tolerable for people in practice, unchecked.
- How edges link to episodes in Graphiti is not confirmed by a fetched page.
- Whether a "withdrawn" state is worth having apart from "rejected" is a design choice, not a research fact.
