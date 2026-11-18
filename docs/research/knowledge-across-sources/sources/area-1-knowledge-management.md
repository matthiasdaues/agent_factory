# Area 1: Personal and Team Knowledge Management

This index covers assignment A1 of the survey. It sorts the 18 source records in `sources/area-1/` by concept. Each statement cites record IDs. The records hold the quotes; this index does not repeat them.

## State of the art

A knowledge tool stores items and the links between them. The sources in this area answer three questions in different ways: where a link is stored, which way it can be followed, and what it records about its origin.

**Links in hypertext.** Bush proposed a link that is written on both items and can be followed from either side. A named trail is a sequence of such links, and a trail can be copied to another person's machine (A1-SR-01). Engelbart added link types and a direction on most links (A1-SR-02). He also used "antecedent links" to trace a statement back to its premises, a form of provenance inside one argument (A1-SR-02). Nelson's Xanadu keeps links outside the documents, makes them two-way, and adds transclusion, a re-use connection that keeps the origin of quoted content visible (A1-SR-03). The Dexter reference model treats a link as a stored component with two or more ends and a direction per end (A1-SR-04, A1-SR-05).

**The Web link.** The Web chose a link that is one-way in the data model and embedded in the source document. Berners-Lee rejected dates, versions and authorship on the link itself. He named two ways to recover the reverse direction: create a reverse link when the link is made, or gather back-links with a background process (A1-SR-07). His 1989 proposal asked for private links and annotations on public information (A1-SR-06). Nelson called the result "fragile ever-breaking one-way links" (A1-SR-03).

**Note graphs.** Luhmann's card index linked notes by fixed note numbers written on the referring note. A keyword register gave entry points, and sources sat in a separate bibliographic section (A1-SR-08, a translation). Obsidian and Logseq document links that are written one-way in the source note and shown in reverse as computed backlinks (A1-SR-09, A1-SR-10). Logseq also documents block embeds, which show and edit a source block in place (A1-SR-10). Neither tool's documentation records who made a link or when (A1-SR-09, A1-SR-10).

**Annotation.** The W3C Web Annotation Data Model stores the annotation as a resource of its own, apart from its target. It records a creator and a creation time, points into the target by quote or position, and can name the version of the target that was meant (A1-SR-18). It grew out of the Open Annotation Community Group drafts of 2012 and 2013 (A1-SR-17).

**Personal information management.** Studies in this field look at how people keep and re-find their own items, mostly through folders and placement (A1-SR-11). The one study recorded here does not treat links or provenance (A1-SR-11).

**Enterprise knowledge management.** The SECI model of Nonaka describes four modes of conversion between tacit and explicit knowledge (A1-SR-12). Critics argue that tacit knowledge cannot be captured, that knowledge management manages information or work practices (A1-SR-14), that the conversion modes lack evidence (A1-SR-15), and that the term "tacit knowledge" is used in at least eight ways (A1-SR-16). In 2009 the proponents restated tacit and explicit knowledge as ends of a continuum (A1-SR-13, abstract only).

## Concept 1: Link direction and storage

This concept asks where a link is kept and from which side it can be followed.

1. **Two-sided trail link, 1945.** The memex writes the link code on both items, so either item recalls the other (A1-SR-01). The sources record no criticism that led to the next step. Gap.
2. **Directed, typed link, 1962.** Most links have a direction, like an arrow, and links carry types (A1-SR-02). No recorded source links a criticism of step 1 to this change. Gap.
3. **External two-way link and transclusion, dated by Nelson to 1960 and 1965.** Links sit outside the documents, run both ways, and re-use is a separate connection (A1-SR-03). The dates are Nelson's own account, and he calls the 1960 design "currently undocumented" (A1-SR-03). Nelson's 1965 paper was not read. Gap for a contemporary source.
4. **Dexter reference model, 1990.** A link is a component with two or more specifiers; each specifier carries a direction (FROM, TO, BIDIRECT, NONE) (A1-SR-04, A1-SR-05). The criticism behind it is that hypertext systems "differ markedly" in their data models, which blocks comparison and interchange (A1-SR-04).
5. **Web link, one-way in the data model, about 1991.** Berners-Lee argues that enforced two-way links can constrain an author, and he asks how a two-way link to a protected database could be made. He proposes reverse links on write or back-links gathered by a background process (A1-SR-07). The date is a lower bound from the page's citation of HT91 (A1-SR-07).
6. **Criticism of the Web link, 1999.** Nelson calls Web links one-way, embedded, and breaking, with no record of change (A1-SR-03). No source in this area shows that this criticism changed the Web standard. Gap.
7. **Computed backlinks in note tools, current documentation.** Obsidian and Logseq store links one-way and compute the reverse view inside one vault or graph (A1-SR-09, A1-SR-10). This matches the background-process option of step 5 (A1-SR-07). Neither tool's documentation cites step 5 or step 6 as its reason. Gap for the criticism that drove this step.

## Concept 2: Information about a link, and the annotation model

This concept asks where the author, date and comment of a connection are recorded.

1. **Comments on typed links in Enquire, 1980; private annotations as a requirement, 1989.** Enquire links have a type and may carry a comment. The proposal asks that users can annotate links and nodes privately (A1-SR-06).
2. **Link metadata rejected on the link, about 1991.** Berners-Lee argues that dating, versioning and authorship on a link turn the link into a node and "perverts the data model". He points such information to the source node or to an annotation node (A1-SR-07).
3. **Open Annotation community drafts, 2012 and 2013.** The group sets out to reconcile two earlier annotation proposals into one RDF-based specification (A1-SR-17). The draft texts were not read. Gap for their content.
4. **W3C Web Annotation Data Model, 2017.** The annotation is a separate resource with body, target, creator and creation time. Selectors and States point into a given version of the target (A1-SR-18). The recorded reasons for change from step 3 are developer-friendly names, more lifecycle metadata, and selectors added "from implementation experience" (A1-SR-18). The specification also notes that a position selector "is very brittle" when the target changes, and recommends a State (A1-SR-18).

## Concept 3: Note references in a card index and in note graphs

This concept asks how one note points to another and to its sources.

1. **Fixed-number references, 1981.** Each note keeps a fixed number. References on a note point to other numbers, a register gives entry points, and sources sit in a bibliographic section (A1-SR-08). The record is a translation, not the German original.
2. **Wiki links, block references and computed backlinks, current documentation.** Links point to a note name or a block ID, and the tool lists incoming links (A1-SR-09, A1-SR-10). Obsidian updates links on rename (A1-SR-09). No recorded tool documentation names the Zettelkasten as its model or names a criticism of step 1. Gap.

## Concept 4: The SECI model of knowledge creation

This concept asks how the proponents formulate knowledge conversion and how critics answer.

1. **Nonaka 1991, Harvard Business Review.** Not read. Gap.
2. **Nonaka 1994, Organization Science.** Not read; the copy at uky.edu failed TLS verification. Its existence and role are recorded by A1-SR-12 and A1-SR-13. Gap for its text.
3. **Nonaka and Takeuchi 1995, The Knowledge-Creating Company.** Not read. Wilson and Gourlay criticise it (A1-SR-14, A1-SR-16). Gap for its text.
4. **SECI, ba and knowledge assets, 2000.** The four modes stay. The authors add ba, a shared context, and knowledge assets as inputs and outputs (A1-SR-12). They keep "justified true belief" as the definition of knowledge but focus on "justified" (A1-SR-12). No recorded source names the criticism that led to this extension. Gap.
5. **Criticism, 2002 to 2006.** Wilson argues that tacit knowledge "cannot be 'captured'" and that Nonaka misread Polanyi (A1-SR-14). Gourlay finds eight uses of "tacit knowledge" in empirical studies (A1-SR-16). He argues that none of the modes has evidence that cannot be explained more simply, and that the model uses "a radically subjective definition of knowledge" (A1-SR-15, abstract only).
6. **Proponents' reply, 2009.** Nonaka and von Krogh restate tacit and explicit knowledge as ends of "a continuum" and say they answer six questions from the debate (A1-SR-13, abstract only). The body of the reply was not read. Gap for which criticism each answer addresses.

## Gaps

**Unreachable sources.**

- The Atlantic page for Bush 1945 blocked automated access. A1-SR-01 uses the 1994 Duchier transcription on an MIT course site.
- Nonaka 1994 at uky.edu failed TLS certificate verification for both curl and WebFetch on 2026-11-18.
- Gourlay 2006 at eprints.kingston.ac.uk did not resolve. A1-SR-15 uses the RePEc abstract.
- Nonaka and von Krogh 2009 at ai.wu.ac.at returned HTTP 403. A1-SR-13 uses the RePEc abstract.
- Tsoukas 2003, "Do we really understand tacit knowledge?", at mba.eci.ufmg.br returned HTTP 404.
- Malone 1983 at typeset.io returned HTTP 403. A1-SR-11 summarises it as a secondary source.
- The Open Annotation draft at openannotation.org/spec/core/ returned only a cookie banner.
- The Dexter repost ends before the link definition. A1-SR-05 covers the link as a secondary source.

**Not covered.**

- Roam Research: no record. No static documentation page was found, and the vendor help is a web application.
- Halasz 1988, "Reflections on NoteCards", which Dexter cites, was not read.
- Nelson's 1965 ACM paper and Engelbart's NLS demonstration of 1968 were not read.
- Luhmann's German original was not compared with the translation.
- Personal information management has one record. Lansdale 1988, Jones, and Whittaker 2011 were not reached.
- Enterprise knowledge management outside SECI has one critic record (A1-SR-14). No recorded source covers knowledge repositories or communities of practice.

**Searches with no result.**

- On 2026-11-18, web searches for a full-text Nonaka 1994, a full-text Gourlay 2006, and a full-text Whittaker 2011 found only the unreachable copies listed above or download portals of unknown status.
- No tool documentation was found that names the Zettelkasten or the Memex as the model for its backlinks. Only Obsidian Help and Logseq docs were checked.
- No source was found that ties a change in the Web link standard to Nelson's criticism.

**Contrary evidence searched.** Critics of SECI were searched for on 2026-11-18 with the terms "critique SECI model Nonaka tacit knowledge" and the Gourlay and Tsoukas titles; A1-SR-14, A1-SR-15 and A1-SR-16 are the result. For the link model, the Berners-Lee design note (A1-SR-07) is the recorded counter-position to Nelson (A1-SR-03). No defence of embedded one-way links beyond A1-SR-07 was searched for.
