# Independent process design

## Recommendation and evidence boundary

Give ideas their own records before they become proposals. Keep source evidence, interpretation, and stakeholder decisions distinct. Generate the searchable graph from those records.

This report compares three proposed designs. None is implemented or approved here. It follows the [research question](../research-question.md#settled-for-this-research), independently of the other investigators. Repository observations below were checked by reading the cited files. No external product or standards claim is relied on. The Concept inventory proposal's standards claims remain unchecked in this task.

## Where ideas enter, get decided, and disappear

Ideas enter before the Factory requires an artifact. VIRGIL permits open conversation, then routes a shaped idea into a proposal, project, spike, or research brief. A chat may end without an artifact. This is a retention gap by design, not evidence that particular conversations were lost. [packages/factory/agents/virgil.md § When the shape becomes clear](../../../../packages/factory/agents/virgil.md#when-the-shape-becomes-clear).

Proposal drafting starts after exploration. It transcribes the conversation, records decisions in an appendix, and sharpens the proposal through grilling. Thus, ideas abandoned before drafting have no mandatory home in this procedure. [packages/factory/skills/draft-proposal/SKILL.md § Procedure](../../../../packages/factory/skills/draft-proposal/SKILL.md#procedure).

Decisions already have useful structure. Proposal appendices distinguish decisions from assumptions and name the decider. Proposal status distinguishes readiness, acceptance, delivery, cancellation, and replacement. Stakeholder acceptance remains a separate step. Neither proposal status nor an assumption proves that every constituent idea was accepted. [packages/factory/rulebooks/templates/proposal.md § Frontmatter and Decisions](../../../../packages/factory/rulebooks/templates/proposal.md#frontmatter); [packages/factory/playbooks/feature-addition.md § Decision Point 0.2](../../../../packages/factory/playbooks/feature-addition.md#decision-point-02--accept).

Transcripts provide another entry. The transcript skill preserves attributed turns, then separately identifies contradictions, unrecorded agreements, uncommitted features, and deferrals. It does not declare shared idea identities across transcripts. [packages/factory/skills/process-transcript/SKILL.md § Steps 2–4](../../../../packages/factory/skills/process-transcript/SKILL.md#step-2--write-the-verbatim-protocol).

History can survive while remaining hard to retrieve. The counter proposal records a choice of one Git ref per ID, then replaces it with one shared ref. A later ADR changes only the rule for projects without a remote. A useful query must return the applicable decision and its predecessors. [docs/proposals/counter-ids.md § Decisions, DEC-12 and DEC-14](../../../proposals/counter-ids.md#decisions); [docs/adr/0033-the-projects-own-repository-holds-the-counter-until-origin-exists.md § Decision](../../../adr/0033-the-projects-own-repository-holds-the-counter-until-origin-exists.md#decision).

Inference: the main gaps are capture before proposals, identity across documents, and retrieval of qualified decisions. More summaries alone would leave those gaps.

## Common process for all three options

Start each retained exploration by retrieving prior ideas, including rejected and deferred ones. Show the idea, applicable decision, reason, source passage, and any changed condition.

Then formulate alternatives. The agent proposes links such as `refines`, `alternative_to`, and `depends_on`. It labels new combinations as suggestions. Existing rejection prompts an explanation of what changed; it does not prohibit reconsideration.

At a topic boundary, capture new ideas and ask the stakeholder to resolve decisions that need authority. Permit an undecided idea. At session close, report captured topics and explicit omissions. Interrupted sessions must remain visibly incomplete.

Treat concept formulation as assembling related ideas around a problem, expected outcome, constraints, alternatives, and unresolved questions. Promote that assembly into the existing proposal when it has enough shape. The proposal remains the authoritative design origin. [packages/factory/playbooks/feature-addition.md § Prerequisites](../../../../packages/factory/playbooks/feature-addition.md#prerequisites).

Use two decision dimensions. A disposition says `undecided`, `do`, `wont_do`, or `defer`. A separate acceptance record says which proposal revision the stakeholder approved. This avoids treating “accept this description” as “implement this idea.” These meanings are proposed conventions requiring confirmation.

Every decision needs a target, scope, actor, reason, evidence, recorded time, and predecessor when it replaces another decision. A deferral also needs an owner and revisit trigger. Resolve conflicts explicitly; never let the latest timestamp silently win.

Every extracted assertion needs a source locator: repository path, full commit SHA, and section or passage identifier; or external object identity and message locator. Uncommitted material needs a retained snapshot and content hash until a commit exists. Preserve multiple origins. A link demonstrates origin, not truth or authority. Missing evidence remains marked missing. Agent interpretation never becomes a stakeholder decision without supporting evidence.

## Option A: annotate source documents

Keep ideas inside the documents where they arose. Build the graph as a disposable projection of explicit annotations.

**Storage and authorship.** Agents add structured Markdown tables beside proposal appendices and transcript comparisons. Tables identify idea mentions, relationships, decision evidence, and superseding references. Verbatim protocols remain untouched. New conversations use one Markdown capture document under `docs/knowledge/sessions/`. An idea identity is its originating document identity plus a stable local anchor. Repeated mentions point back to that identity.

**Query.** A deterministic script parses these tables and produces a linked Markdown result. A proposal session searches by topic, aliases, and relationships, then opens the cited passages. The graph contains only annotated material; an ingestion inventory exposes unprocessed documents.

**Decision changes.** Append a decision at its new source and explicitly reference the earlier decision. The generated view resolves the chain. Existing proposal decisions remain authoritative in their appendices. Annotations point to them without creating competing decisions.

**Fit and cost.** Markdown remains canonical. Agents interpret meaning; scripts check structure, anchors, and decision chains. Existing documents retain their identities. New capture documents require a registered counter prefix. All five CLIs consume the same files and command contract, subject to the integration gap below.

This option changes the fewest authoring habits. However, idea identity remains tied to document organization. Cross-document conflicts, moved anchors, and scattered annotations make maintenance harder.

## Option B: independent idea records

Store one idea per Markdown record. Let that identity survive proposal rejection, replacement, and reuse.

**Storage and authorship.** Agents write `docs/knowledge/ideas/IDEA-<number>.md`. YAML frontmatter holds schema version, ID, title, aliases, and typed links. The body holds the bounded idea, source references, and decision history. A record describes one proposal for change or one concept, not a whole conversation. Sources remain in their existing homes. Imported sources receive separate Markdown descriptors under `docs/knowledge/sources/`.

Each source reference identifies the passage and its revision. Each relation carries its own evidence and whether a human confirmed it. Duplicate candidates stay separate until a reviewed merge establishes a retained ID and redirect. A split keeps the original record and links its narrower successors.

**Query.** A deterministic command validates records and builds a disposable index. It returns exact matches, alias matches, related ideas, unresolved conflicts, and rejected or deferred alternatives. Each result links to its record and evidence. The agent reads that bounded set before proposing alternatives. Every result reports the indexed scope and revision. Zero matches do not establish that an idea was never discussed.

**Decision changes.** The record owns decisions made before a proposal exists. Once a proposal owns a decision, the record references its appendix row and revision. The index derives its current view from that evidence. A later decision appends a superseding entry; it does not erase the earlier reason. Contradictory decisions without explicit precedence produce a conflict. Proposal acceptance applies only to explicitly linked ideas and scope.

**Fit and cost.** Register `IDEA` and, if needed, a source-descriptor prefix with the existing allocator. Use document-local anchors for decision rows. Agents write meaning; deterministic gates validate IDs, links, source locators, and supersession cycles. CLI integrations share the same records and query command.

This option directly supports ideas that appear in several proposals. Its main cost is curation: duplicate detection, splitting broad ideas, and preventing idea descriptions from becoming parallel specifications.

## Option C: append-only session ledgers

Store the sequence of recorded assertions and decisions as the authority. Generate idea pages from that sequence.

**Storage and authorship.** Each capture session gets a Markdown ledger under `docs/knowledge/sessions/`. Structured entries record `idea_created`, `source_linked`, `relation_asserted`, `decision_recorded`, and `assertion_corrected`. Agents author entries from evidence. A deterministic validator checks them against the existing ledger set. Generated idea pages are disposable and never edited directly.

**Query.** A deterministic reducer reads all ledgers and reconstructs current or historical idea views. The proposal session receives the same bounded result format as Option B. It can also ask what the recorded decision was before a specified revision.

**Decision changes.** Corrections and reversals become new entries referencing the entries they amend. Entries about proposal or ADR decisions cite those authoritative records; they do not independently approve scope. Concurrent incompatible decisions remain a conflict until an explicit resolution references both. Ordering follows predecessor references, not wall-clock time. Gates reject edits to published entries, while allowing new correction entries.

**Fit and cost.** Markdown ledgers stay in Git. New session and idea IDs require counter prefixes; event identities combine session ID and local anchor. Agents make assertions; scripts validate and replay them. All five CLIs use the same append and query contracts, subject to the integration gap below.

This option makes historical reconstruction explicit and suits repeated ingestion. It requires more machinery: replay rules, event-version migration, correction semantics, and protections against editing published history. Human review spans more files than Option B.

## Fit with Factory constraints

All three options keep semantic authoring separate from structural validation. A gate can reject missing evidence references. It cannot prove that extraction found every idea or interpreted a speaker correctly. The stakeholder or an independent reviewer checks those meanings. This follows [packages/factory/rulebooks/rules.md § Foundational principles](../../../../packages/factory/rulebooks/rules.md#foundational-principles).

New prefixes are design work, not available commands. The current registry has twelve prefixes and excludes proposal-local findings from the counter. Extend the registry and allocator together before creating persistent graph IDs. Never allocate IDs by scanning the largest filename. [packages/factory/rulebooks/conventions/id-prefixes.md](../../../../packages/factory/rulebooks/conventions/id-prefixes.md).

Five-CLI parity needs separate verification. The installer names Claude Code, Codex, Copilot, Pi, and OpenCode, but currently gives OpenCode only an explicitly selected guard plugin. It excludes OpenCode from the default set. The plugin also says its envelope has not been checked against a real OpenCode session. [packages/factory/scripts/init-factory, lines 174–187](../../../../packages/factory/scripts/init-factory); [packages/factory/config/plugins/agent-factory.ts, lines 7–15](../../../../packages/factory/config/plugins/agent-factory.ts).

Therefore, none of these designs depends on native CLI memory, automatic transcript hooks, or an external graph service. Each requires a common file-and-command contract, with an integration check in every CLI. Automatic capture across the five CLIs remains unchecked.

All options require an explicit capture path beyond today's VIRGIL boundaries. VIRGIL permits no artifact for chat and at most one seed document per session. A dedicated capture activity needs declared outputs; it cannot quietly inherit permission to write many records. [packages/factory/agents/virgil.md § Boundaries](../../../../packages/factory/agents/virgil.md#boundaries).

The Concept inventory draft addresses knowledge obligations, including unknowns, owners, and resolution points. It does not establish this graph or approve its implementation. Keep obligation state separate from idea disposition: “availability target unknown” differs from “do not implement redundancy.” [docs/proposals/concept-stage-knowledge-inventory.md § Knowledge-obligation register](../../../proposals/concept-stage-knowledge-inventory.md#knowledge-obligation-register).

Also distinguish this proposed concept formulation from the specification-producing CONCEPT cycle described in [docs/adr/0018-concept-internal-sequence-is-agent-owned.md § Context](../../../adr/0018-concept-internal-sequence-is-agent-owned.md#context). A shared word does not establish a shared workflow.

## Recommendation and smallest proof

Choose Option B for a bounded pilot. It gives an idea a stable home without requiring the event-replay machinery of Option C.

Use the counter discussion as the concrete case. Option A retrieves linked annotations across the proposal and ADRs. Option B presents stable idea records with their supporting decisions. Option C reconstructs those records from ledger entries. Option B makes repeated comparison easiest to inspect; that is a design judgment, not a measured result.

The pilot should prove retrieval and decision history before adding bulk ingestion or semantic search:

1. Select the counter proposal, [the original counter decision](../../../adr/0031-ids-come-from-one-git-ref-with-leased-pushes.md#decision), and [its local-counter amendment](../../../adr/0033-the-projects-own-repository-holds-the-counter-until-origin-exists.md#decision) as a closed corpus. Record its limits. Use existing document-and-row identities for a disposable trial; allocate no production graph IDs yet.
2. Author a few trial idea records covering the shared counter, one ref per ID, and operation without `origin`. Preserve the original decisions and later amendments. Store trial records inside one pilot dossier.
3. Add one unaccepted idea from the Concept inventory draft. Verify that retrieval never presents it as approved policy.
4. Ask a fresh session: “Can a new project without `origin` allocate IDs?” Require the local-counter decision, its configuration condition, and the superseded rule. Ask whether one ref per ID remains chosen. Require the replacement decision and its reason.
5. Check source locators and precedence mechanically. Introduce a broken locator and two conflicting decisions in the disposable fixture. Require a missing-source result and an unresolved conflict, respectively.
6. Have a human compare answers with the cited passages. The pilot passes only if both historical answers are correct, draft status survives, and neither injected defect disappears.

The later counter amendment supplies the first answer. [docs/adr/0033-the-projects-own-repository-holds-the-counter-until-origin-exists.md § Decision](../../../adr/0033-the-projects-own-repository-holds-the-counter-until-origin-exists.md#decision). This research only specifies the pilot; it creates no fixtures, code, or proposal changes.

## Open questions

- What sources count toward “every idea,” and who authorizes capture of conversations that currently leave no artifact?
- Who confirms idea merges, splits, and inferred relationships? What review effort is acceptable?
- Does “accept” mean agreement with an idea, approval of proposal scope, or both? Which roles may make each decision?
- What retention and access rules apply to imported messages and copied excerpts? How should inaccessible or deleted evidence appear?
- How should proposal decision amendments update references without creating a second authority?
- Does the pilot justify semantic retrieval, or are aliases and explicit links sufficient? Retrieval quality and review cost remain unmeasured.
- When will OpenCode have the orientation and capture integration needed for five-CLI parity? This task checked source declarations, not live CLI behavior.
