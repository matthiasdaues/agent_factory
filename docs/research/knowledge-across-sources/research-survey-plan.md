# Research Survey Plan — Knowledge Across Sources

The plan follows [research-brief.json](research-brief.json). It splits the survey by the four scope areas of the brief, so no two assignments research the same concept. All four assignments run in parallel as one wave.

## Research Questions

1. Area 1: How did personal and team knowledge management develop from the Memex and hypertext through the Zettelkasten to current note graphs and enterprise knowledge management, and how does each step handle sources, links, and provenance?
2. Area 2: How do claim detection, claim matching, and fact-checking pipelines work, what does the ClaimReview markup record, and how are corrections and retractions recorded and followed?
3. Area 3: How do email, chat, and meeting transcripts identify messages, threads, and speakers, and how are decisions and action items extracted from meetings?
4. Area 4: How can a downstream source's reuse of a primary report be classified as verbatim, altered, reframed, or independent, and which methods does the literature offer for each class?
5. Across areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?

## Search Angles

- The original paper or specification for each concept, then the papers, comments, or decisions that criticized or changed it
- Peer-reviewed surveys as the overview of each area, such as surveys of automated fact-checking, conversation disentanglement, and framing research
- RFC Editor documents and their "Obsoletes" and "Updates" headers, which record each revision of email message identity
- Shared-task overview papers, such as CLEF CheckThat!, FEVER, SemEval, and PAN, which record how task definitions changed from year to year
- Project documentation and schema pages for note tools, chat export formats, and ClaimReview, used for stated features only
- Critiques and replies, such as the debate on framing as a "fractured paradigm" and the criticism of the SECI model

## Source Targets

- Bush 1945 "As We May Think", Engelbart, Nelson on Xanadu and transclusion, the Dexter hypertext reference model, Halasz on the issues of hypermedia systems, and Luhmann on the Zettelkasten
- Peer-reviewed work on personal information management and enterprise knowledge management, such as Nonaka and Takeuchi and its critics, and the W3C Web Annotation Data Model
- Documentation of current note graph tools, such as Obsidian, Logseq, and Roam, for their link and backlink models
- ClaimBuster, CLEF CheckThat! overview papers from 2018 onward, FEVER, claim matching papers, and surveys of automated fact-checking from 2020 onward
- schema.org pages for ClaimReview and MediaReview, the IFCN code of principles, and the NISO Communication of Retractions, Removals, and Expressions of Concern (CREC) recommended practice
- RFC 822, RFC 2822, RFC 5322, RFC 5256, the JWZ threading description, XMPP XEP documents for stable message IDs and archives, and the Matrix specification
- Official export format documentation of chat services, and papers on conversation disentanglement, speaker diarization, and meeting corpora such as AMI, ICSI, and QMSum
- Text reuse work, such as the METER corpus, Memetracker, and studies of news agency copy in newspapers, and framing work from Goffman and Entman onward
- Stance detection work, such as SemEval-2016 Task 6 and the Fake News Challenge, and work on tracing the origin of a claim

## Assignments

Each assignment declares agent, tier, independent session, a unique output, and a bounded task. The output is a record folder, an ID prefix, and one area index beside the folder, as [source-research](../../../packages/factory/skills/source-research/SKILL.md#record-file) defines. Every task carries the same three requirements:

- For each hardened concept in the area, record the sequence of formulations and the criticism that drove each change, with a source for each step.
- Put the source's own words in straight double quotes in the Evidence section, because `concept-history-check` anchors only on quoted words.
- Mark each source primary or secondary, and state what it shows and what it does not show.

Three boundaries keep the areas apart. Area 4 owns stance detection and the tracing of a claim's origin, so area 2 does not research them. Area 3 owns speaker attribution in transcripts. Graph data models and PROV-O belong to the earlier knowledge-graph-state-of-the-art survey and appear only as context.

| ID  | Agent      | Tier     | Area                                   | Output                                                                                | Independent Session |
| --- | ---------- | -------- | -------------------------------------- | ------------------------------------------------------------------------------------- | ------------------- |
| A1  | researcher | standard | personal and team knowledge management | `sources/area-1/`, prefix `A1-SR-`, index `sources/area-1-knowledge-management.md`    | false               |
| A2  | researcher | standard | claims across news                     | `sources/area-2/`, prefix `A2-SR-`, index `sources/area-2-claims-across-news.md`      | false               |
| A3  | researcher | standard | email, chat, and meeting transcripts   | `sources/area-3/`, prefix `A3-SR-`, index `sources/area-3-email-chat-transcripts.md`  | false               |
| A4  | researcher | standard | claim propagation and framing          | `sources/area-4/`, prefix `A4-SR-`, index `sources/area-4-propagation-and-framing.md` | false               |

## Stop Conditions

- Each of the four assignments has recorded sources for the main concepts of its area, and `source-record-check` exits 0 on its folder.
- At least five concepts have a recorded sequence of formulations, with the criticism and a source for each step.
- Area 4 has at least one recorded method, or a recorded gap, for each of the four reuse classes: verbatim, altered, reframed, and independent.
- A secondary source is marked as secondary and used only where no primary source is reachable.
- An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index.

## Structured Block

The block below is the plan in the shape of `research-survey-plan.schema.json`. The tasks in `assignments` are the full text each researcher receives.

```json
{
  "research_questions": [
    "Area 1: How did personal and team knowledge management develop from the Memex and hypertext through the Zettelkasten to current note graphs and enterprise knowledge management, and how does each step handle sources, links, and provenance?",
    "Area 2: How do claim detection, claim matching, and fact-checking pipelines work, what does the ClaimReview markup record, and how are corrections and retractions recorded and followed?",
    "Area 3: How do email, chat, and meeting transcripts identify messages, threads, and speakers, and how are decisions and action items extracted from meetings?",
    "Area 4: How can a downstream source's reuse of a primary report be classified as verbatim, altered, reframed, or independent, and which methods does the literature offer for each class?",
    "Across areas: Which concepts went through several documented rounds of formulation, criticism, and reformulation, and what criticism drove each change?"
  ],
  "search_angles": [
    "The original paper or specification for each concept, then the papers, comments, or decisions that criticized or changed it",
    "Peer-reviewed surveys as the overview of each area, such as surveys of automated fact-checking, conversation disentanglement, and framing research",
    "RFC Editor documents and their Obsoletes and Updates headers, which record each revision of email message identity",
    "Shared-task overview papers, such as CLEF CheckThat!, FEVER, SemEval, and PAN, which record how task definitions changed from year to year",
    "Project documentation and schema pages for note tools, chat export formats, and ClaimReview, used for stated features only",
    "Critiques and replies, such as the debate on framing as a fractured paradigm and the criticism of the SECI model"
  ],
  "source_targets": [
    "Bush 1945 As We May Think, Engelbart, Nelson on Xanadu and transclusion, the Dexter hypertext reference model, Halasz on the issues of hypermedia systems, and Luhmann on the Zettelkasten",
    "Peer-reviewed work on personal information management and enterprise knowledge management, such as Nonaka and Takeuchi and its critics, and the W3C Web Annotation Data Model",
    "Documentation of current note graph tools, such as Obsidian, Logseq, and Roam, for their link and backlink models",
    "ClaimBuster, CLEF CheckThat! overview papers from 2018 onward, FEVER, claim matching papers, and surveys of automated fact-checking from 2020 onward",
    "schema.org pages for ClaimReview and MediaReview, the IFCN code of principles, and the NISO CREC recommended practice on retractions",
    "RFC 822, RFC 2822, RFC 5322, RFC 5256, the JWZ threading description, XMPP XEP documents for stable message IDs and archives, and the Matrix specification",
    "Official export format documentation of chat services, and papers on conversation disentanglement, speaker diarization, and meeting corpora such as AMI, ICSI, and QMSum",
    "Text reuse work, such as the METER corpus, Memetracker, and studies of news agency copy in newspapers, and framing work from Goffman and Entman onward",
    "Stance detection work, such as SemEval-2016 Task 6 and the Fake News Challenge, and work on tracing the origin of a claim"
  ],
  "assignments": [
    "A1 | agent: researcher | tier: standard | independent_session: false | area: personal and team knowledge management | output: folder sources/area-1/, ID prefix A1-SR-, index sources/area-1-knowledge-management.md | task: Personal and team knowledge management. Trace the lineage from Bush's Memex (1945) through Engelbart, Nelson's Xanadu and transclusion, and the Dexter hypertext reference model to the Web's one-way link, then from Luhmann's Zettelkasten to current note graphs with backlinks, such as Obsidian, Logseq, and Roam. Cover personal information management and enterprise knowledge management, including the SECI model and its critics, and the W3C Web Annotation Data Model. For each step, record how it handles sources, links, and provenance. Use tool documentation for stated features only, never vendor marketing as evidence of capability or adoption. Do not research graph data models or PROV-O; the knowledge-graph-state-of-the-art survey covers them. For each hardened concept in the area, such as the link model or the SECI model, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section. Mark each source primary or secondary. State for each source what it shows and what it does not show. Record failed searches and gaps in the area index.",
    "A2 | agent: researcher | tier: standard | independent_session: false | area: claims across news | output: folder sources/area-2/, ID prefix A2-SR-, index sources/area-2-claims-across-news.md | task: Claims across news. Cover check-worthy claim detection from ClaimBuster onward, the CLEF CheckThat! task definitions from 2018 onward, claim matching against already fact-checked claims, fact-checking pipelines and datasets such as FEVER, and language-model fact-checking from 2020 onward. Record what the schema.org ClaimReview and MediaReview types contain and how fact-checkers use them. Record how news corrections and retractions are recorded and followed, such as the IFCN code of principles and the NISO CREC recommended practice. Do not research stance detection or the tracing of a claim's origin; area 4 owns them. For each hardened concept in the area, such as the definition of a check-worthy claim, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section. Mark each source primary or secondary. State for each source what it shows and what it does not show. Record failed searches and gaps in the area index.",
    "A3 | agent: researcher | tier: standard | independent_session: false | area: email, chat, and meeting transcripts | output: folder sources/area-3/, ID prefix A3-SR-, index sources/area-3-email-chat-transcripts.md | task: Email, chat, and meeting transcripts as sources. Cover message identity and threading in email, from RFC 822 through RFC 2822 to RFC 5322 Message-ID, In-Reply-To, and References, plus RFC 5256 and the JWZ threading algorithm. Cover stable message IDs and thread models in chat, such as XMPP XEP documents and the Matrix specification, and the official export formats of major chat services. Cover conversation disentanglement, speaker attribution and diarization, and the extraction of decisions and action items from meetings, with corpora such as AMI, ICSI, and QMSum. For each hardened concept in the area, such as the Message-ID rules or the disentanglement task definition, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section. Mark each source primary or secondary. State for each source what it shows and what it does not show. Record failed searches and gaps in the area index.",
    "A4 | agent: researcher | tier: standard | independent_session: false | area: claim propagation and framing | output: folder sources/area-4/, ID prefix A4-SR-, index sources/area-4-propagation-and-framing.md | task: Claim propagation and framing. Find how the literature classifies a downstream outlet's reuse of a primary report as verbatim, altered, reframed, or independently reported, and which methods detect each class. Cover text reuse detection, such as the METER corpus, PAN, Memetracker, and studies of news agency copy in newspapers. Cover framing theory from Goffman and Entman onward with its criticism and its computational measurement, such as the Media Frames Corpus and SemEval framing tasks. Cover stance detection, such as SemEval-2016 Task 6 and the Fake News Challenge, and the detection of sentiment shift between versions of a claim. Cover the tracing of a claim's origin in fact-checking. For each hardened concept in the area, such as the definition of a frame, record the sequence of formulations and the criticism that drove each change, with a source for each step. Put the source's own words in straight double quotes in the Evidence section. Mark each source primary or secondary. State for each source what it shows and what it does not show. Record for each reuse class at least one method or a recorded gap. Record failed searches and gaps in the area index."
  ],
  "stop_conditions": [
    "Each of the four assignments has recorded sources for the main concepts of its area, and source-record-check exits 0 on its folder.",
    "At least five concepts have a recorded sequence of formulations, with the criticism and a source for each step.",
    "Area 4 has at least one recorded method, or a recorded gap, for each of the four reuse classes: verbatim, altered, reframed, and independent.",
    "A secondary source is marked as secondary and used only where no primary source is reachable.",
    "An assignment stops searching when further sources are unlikely to change its findings, and records its failed searches as gaps in its area index."
  ]
}
```
