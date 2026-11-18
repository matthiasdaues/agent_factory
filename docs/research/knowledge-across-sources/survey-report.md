# Survey Report: Knowledge Across Sources

This report answers [research-brief.json](research-brief.json) in survey mode. It uses only the 77 source records under [sources/](sources/), cited by record ID. It reports what the sources document. It gives no verdict on whether any concept holds; that verdict belongs to a later falsification study.

## 1. Answer

The surveyed methods capture and link knowledge in separate traditions, and no recorded system joins them. Hypertext and note tools link items but record little about who made a link or when (A1-SR-07, A1-SR-09, A1-SR-10). The W3C annotation model records creator, time, and the exact target version (A1-SR-18). Email and chat identify messages and threads by header fields and event IDs, which are usable provenance anchors with known defects in practice (A3-SR-05, A3-SR-06, A3-SR-11, A3-SR-14). Fact-checking detects, matches, and verifies claims, and publishes verdicts as ClaimReview markup (A2-SR-07, A2-SR-11, A2-SR-14). Meeting research labels decisions and action items as roles of utterances (A3-SR-20, A3-SR-21).

For claim propagation, the records hold mature methods for verbatim reuse and younger methods for altered meaning. This survey found no recorded method for two needs. The first is a pairwise test of reframing between a source and its reuse by another outlet. The nearest record, MediaSpin, labels bias added or removed between two versions of one headline from the same outlet (A4-SR-17). The second need is to separate independent reporting from undisclosed reuse of a shared source, a limit that three records name (A4-SR-04, A4-SR-14, A4-SR-15).

The table in section 3 ranks ten concepts that meet the entry rule of at least three formulations and two recorded criticisms. Three of the top four come from email and chat identity, where standards record each revision, and one comes from stance research. The concept Frame ranks last of the ten, because most of its anchors are secondary sources.

## 2. State of the art by area

### 2.1 Personal and team knowledge management

A knowledge tool stores items and the links between them. The sources differ on three questions: where a link is stored, which way it can be followed, and what it records about its origin. Bush wrote a link on both items, so either item recalls the other (A1-SR-01). Engelbart gave links a type and, mostly, a direction. His "antecedent links" trace a statement to its premises, a form of provenance inside one argument (A1-SR-02). Nelson's Xanadu keeps two-way links outside the documents and adds transclusion, a re-use connection that keeps the origin of a quotation visible (A1-SR-03). The Dexter model stores links as components of their own and addresses their ends through anchors with stable IDs (A1-SR-04, A1-SR-05).

The Web chose a link that is one-way in the data model. Berners-Lee rejected dates, versions, and authorship on the link and pointed them to an annotation node (A1-SR-07). Obsidian and Logseq write links one-way and compute backlinks inside one vault or graph. Neither tool's documentation records who made a link or when (A1-SR-09, A1-SR-10). Luhmann's card index linked notes by fixed numbers and kept sources in a separate bibliographic section; the record is a translation (A1-SR-08).

The W3C Web Annotation Data Model stores the annotation apart from its target, with creator, creation time, a quote selector, and a State that names the version of the target (A1-SR-18). It grew out of the Open Annotation drafts of 2012 and 2013 (A1-SR-17).

Personal information management, in the one recorded study, looks at folders and placement and does not treat links or provenance (A1-SR-11). In enterprise knowledge management, the SECI model describes four modes of conversion between tacit and explicit knowledge (A1-SR-12). Critics argue that tacit knowledge cannot be captured and that knowledge management manages information or work practices (A1-SR-14). They also find eight uses of the term "tacit knowledge" (A1-SR-16) and no evidence for the modes that a simpler account cannot explain (A1-SR-15, abstract only).

### 2.2 Claims across news

Automated fact-checking runs as a pipeline. A 2022 survey names three stages: claim detection, evidence retrieval, and verification with a verdict and a justification (A2-SR-11). CheckThat! adds a check against claims that were fact-checked before (A2-SR-07, A2-SR-08). Claim matching ranks verified claims for a new claim (A2-SR-07). Meedan widens it to any pair of messages that one fact-check can serve, in five languages (A2-SR-10).

Verification datasets moved from synthetic claims to real ones. FEVER alters Wikipedia sentences (A2-SR-03), and a claim-only model predicts its labels without evidence (A2-SR-06). AVeriTeC uses real claims from fact-checkers and allows only evidence published before the claim (A2-SR-12). Language-model checking began closed-book in 2020 and stayed below systems with retrieval (A2-SR-09). In a 2024 study, GPT agents with web search did better than the same models without it, with accuracy that varied by language and verdict (A2-SR-13).

Fact-checkers publish verdicts as schema.org ClaimReview. A ClaimReview holds a claim summary, the reviewed item, and a rating (A2-SR-14). A Claim can carry its appearances and its first appearance, but schema.org defines no relation between claims (A2-SR-14). Ratings are not standard across fact-checkers (A2-SR-15). Google Search is phasing out ClaimReview display, and Fact Check Explorer keeps it (A2-SR-15). MediaReview records fact-checks of images and video with a link to the original (A2-SR-16, A2-SR-17).

Corrections have weaker records than verdicts. The IFCN code asks signatories to publish and follow a corrections policy (A2-SR-18). A news article can point to a correction through the schema.org `correction` property, which has no field for kind or severity (A2-SR-19). NISO CREC gives scholarly retractions detailed metadata and leaves corrections out of scope (A2-SR-20). No record shows a machine-readable correction to a fact-check.

### 2.3 Email, chat, and meeting transcripts

An email message identifies itself by one `Message-ID`, which must be globally unique. A new version of a message gets a new identifier (A3-SR-04, A3-SR-05). A reply names its parent in `In-Reply-To` and its ancestors in `References`, built from the parent's `References` plus the parent's `Message-ID` (A3-SR-04). That rule came from Usenet (A3-SR-03). Mail software did not follow the rules reliably, so threading code must tolerate missing and contradictory headers (A3-SR-06, A3-SR-07). The IMAP `REFERENCES` algorithm formalizes the Netscape algorithm. When a message has no usable `References`, the algorithm takes the first valid Message-ID in `In-Reply-To` as the parent (A3-SR-07).

Chat protocols separate message identity from conversation identity. XMPP has an opaque `<thread/>` value per conversation (A3-SR-08). Its stable message ID is an Experimental extension and is valid only within the scope of the entity that assigned it (A3-SR-10). Matrix derives the event ID from a hash of the event (A3-SR-11), and its threads are flat (A3-SR-12). Slack identifies a message by channel plus `ts` and builds one level of threads from `thread_ts` (A3-SR-14). The official Slack export does not document thread fields and keeps edits and deletions only under a matching retention policy (A3-SR-13).

Conversation disentanglement splits one chat stream into conversations. Its current task labels reply links and takes each connected component as a conversation (A3-SR-16). Speaker diarization answers "who spoke when" without naming the speakers (A3-SR-22). AMI records one close-talking channel per speaker and links human summaries, with decision and action headings, to dialogue acts (A3-SR-17). Decision and action-item detection label the roles of utterances, such as issue, proposal, and agreement (A3-SR-20, A3-SR-21). One benchmark, QMSum, restates meeting summarization as answers to queries (A3-SR-18).

### 2.4 Claim propagation and framing

No recorded source has one scheme with the four classes verbatim, altered, reframed, and independently reported. Each class lives in a different research line with its own unit of analysis. Section 4 sorts the methods by class.

Text reuse detection on news handles verbatim and lightly edited copy. METER labels stories as wholly, partially, or non-derived from agency copy (A4-SR-01). Boumans et al. find that up to 75% of Dutch online news articles come from the agency, much of it verbatim (A4-SR-04). Memetracker groups the variants of quoted phrases across outlets (A4-SR-03). Changes of meaning are measured by hand coding of claim strength (A4-SR-14) and by a learned score of information change (A4-SR-13).

Framing research labels the frame of one text: 15 generic dimensions in the Media Frames Corpus (A4-SR-09), 14 of them in nine languages in SemEval-2023 (A4-SR-10). MediaSpin labels bias that an edit adds to or removes from a headline, with both versions from the same outlet (A4-SR-17). Stance detection labels a text against a target (A4-SR-11) or an article against a headline (A4-SR-12). Stance and sentiment are different signals (A4-SR-11). Fact-checking tools match repeats of a claim to an existing fact-check (A4-SR-16). Tracing a claim's origin has one formal treatment in the records, a provenance graph whose authors state that the problem is not solved (A4-SR-15).

## 3. Hardened concepts

`concept-history-check` produced the table below from the files in [histories/](histories/). The rank rests on the share of anchors on primary records, then the share of formulations followed by a recorded criticism, then the number of formulations. A concept below the entry rule has fewer than three formulations or fewer than two recorded criticisms.

| Rank | Concept                                           | Area                                      | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                                                              |
| ---- | ------------------------------------------------- | ----------------------------------------- | ------ | ---------- | --------------- | ------------------ | -------------------------------------------------------------------- |
| 1    | In-Reply-To and References                        | 3. Email, chat, and meeting transcripts   | 3      | 3          | 100%            | 100%               | A3-SR-02, A3-SR-06, A3-SR-03, A3-SR-04, A3-SR-07                     |
| 2    | The Matrix event ID                               | 3. Email, chat, and meeting transcripts   | 3      | 2          | 100%            | 100%               | A3-SR-11                                                             |
| 3    | The stance-detection task                         | 4. Claim propagation and framing          | 3      | 2          | 100%            | 100%               | A4-SR-11, A4-SR-12                                                   |
| 4    | The Message-ID rule                               | 3. Email, chat, and meeting transcripts   | 5      | 2          | 100%            | 50%                | A3-SR-01, A3-SR-02, A3-SR-06, A3-SR-03, A3-SR-04, A3-SR-07, A3-SR-05 |
| 5    | Information about a link and the annotation model | 1. Personal and team knowledge management | 3      | 2          | 100%            | 50%                | A1-SR-06, A1-SR-07, A1-SR-18                                         |
| 6    | Measuring a frame in text                         | 4. Claim propagation and framing          | 3      | 2          | 100%            | 50%                | A4-SR-09, A4-SR-10                                                   |
| 7    | Text reuse class                                  | 4. Claim propagation and framing          | 3      | 2          | 100%            | 50%                | A4-SR-01, A4-SR-02, A4-SR-04                                         |
| 8    | Link direction and storage                        | 1. Personal and team knowledge management | 6      | 2          | 100%            | 40%                | A1-SR-01, A1-SR-03, A1-SR-02, A1-SR-04, A1-SR-07, A1-SR-09           |
| 9    | Check-worthy claim                                | 2. Claims across news                     | 4      | 4          | 88%             | 100%               | A2-SR-02, A2-SR-04, A2-SR-08, A2-SR-05, A2-SR-11                     |
| 10   | Frame                                             | 4. Claim propagation and framing          | 4      | 3          | 29%             | 100%               | A4-SR-06, A4-SR-07, A4-SR-08                                         |

Below the entry rule (at least 3 formulations and 2 recorded criticisms):

| Rank | Concept                                | Area                                      | Rounds | Criticisms | Primary anchors | Criticism coverage | Records                      |
| ---- | -------------------------------------- | ----------------------------------------- | ------ | ---------- | --------------- | ------------------ | ---------------------------- |
| -    | Claim provenance                       | 4. Claim propagation and framing          | 2      | 2          | 100%            | 100%               | A2-SR-01, A4-SR-15           |
| -    | Information change in an altered claim | 4. Claim propagation and framing          | 2      | 1          | 100%            | 100%               | A4-SR-14, A4-SR-13           |
| -    | Language-model fact-checking           | 2. Claims across news                     | 2      | 2          | 100%            | 100%               | A2-SR-09, A2-SR-13           |
| -    | The decision-detection task            | 3. Email, chat, and meeting transcripts   | 2      | 1          | 100%            | 100%               | A3-SR-19, A3-SR-21           |
| -    | The disentanglement task               | 3. Email, chat, and meeting transcripts   | 2      | 2          | 100%            | 100%               | A3-SR-15, A3-SR-16           |
| -    | Fact-checking as a verification task   | 2. Claims across news                     | 3      | 1          | 100%            | 50%                | A2-SR-01, A2-SR-03, A2-SR-12 |
| -    | The diarization metric                 | 3. Email, chat, and meeting transcripts   | 3      | 1          | 100%            | 50%                | A3-SR-22                     |
| -    | SECI model of knowledge creation       | 1. Personal and team knowledge management | 2      | 1          | 67%             | 100%               | A1-SR-12, A1-SR-14, A1-SR-13 |

The check reads "primary" from each record's `source_family` field. Four records are primary for their own work but secondary for an earlier formulation they describe: A1-SR-03, A3-SR-22, A4-SR-09, and A4-SR-12. The sections below name each step that reaches the report this way.

### 3.1 In-Reply-To and References

RFC 822 let both fields hold any sequence of free phrases and message identifiers (A3-SR-02). RFC 1036 made `References` for news an ordered ancestor list (A3-SR-03). RFC 2822 restricted both fields to identifiers, adopted the news rule for mail, and assumed a single parent (A3-SR-04). The criticisms come from practice: a header survey and the Netscape threading author (A3-SR-06), and the IMAP threading standard (A3-SR-07). No source presents any of them as the cause of the next change. RFC 5322 states that readers still parse the phrase forms as obsolete syntax and ignore their phrases (A3-SR-05). The history ends at RFC 2822, because A3-SR-04 did not record the obsolete syntax of RFC 2822. So the records do not show whether the RFC 5322 rule is new. History: [reply-references.json](histories/reply-references.json).

### 3.2 The Matrix event ID

Room versions 1 and 2 use an opaque ID with a domain (A3-SR-11). Duplicate IDs led to an ID computed as the hash of the event in room version 3. Client and proxy trouble with the `/` character led to URL-safe Base64 in room version 4 (A3-SR-11). The specification states each criticism as the reason for the next version. All three steps come from one record and carry its publication date, because the record gives no date for each version. That date is itself unconfirmed (A3-SR-11). History: [matrix-event-id.json](histories/matrix-event-id.json).

### 3.3 The stance-detection task

SemEval-2016 defines the task as finding an author's position towards a target (A4-SR-11). FNC-1 moves to the stance of an article towards a headline (A4-SR-12). The FNC-1 definition reaches the report only through Hanselowski et al. Their criticism, that the FNC-1 metric favours the majority class, led to class-wise and macro-averaged F1 (A4-SR-12). The history counts that change of scoring as a formulation of the task, not of stance itself. Human raters agree poorly on the three related classes, κ = .218 (A4-SR-12). History: [stance.json](histories/stance.json).

### 3.4 The Message-ID rule

RFC 733 gives each version of a message a unique identifier, guaranteed by the host that generates it (A3-SR-01). RFC 822 keeps that meaning and writes the identifier in address form (A3-SR-02). RFC 1036 forbids reuse and treats foreign identifiers as opaque (A3-SR-03). RFC 2822 requires global uniqueness and lets the sender's intent decide identity (A3-SR-04). RFC 5322 allows one written form only (A3-SR-05). Two criticisms are recorded: identifiers and addresses share one syntax (A3-SR-06), and quoting allows several forms of one identifier (A3-SR-07). The link from the second criticism to RFC 5322 is an inference; RFC 5322 gives no reason (A3-SR-05). History: [message-id-rule.json](histories/message-id-rule.json).

### 3.5 Information about a link and the annotation model

Enquire links carry a type and a comment (A1-SR-06). Berners-Lee rejects link metadata because it "perverts the data model" and points it to an annotation node (A1-SR-07). The W3C model makes the annotation a resource with body, target, creator, and time (A1-SR-18). The W3C text calls its own position selector "very brittle" and recommends a State (A1-SR-18). The Open Annotation drafts of 2012 and 2013 lie between the second and third steps. Their content was not read, so they are not a step (A1-SR-17). History: [link-information-and-annotation.json](histories/link-information-and-annotation.json).

### 3.6 Measuring a frame in text

Issue-specific codebooks come first. They are known through their critic, the Media Frames Corpus paper, which says they do not allow comparison across issues (A4-SR-09). The paper replaces them with generic framing dimensions (A4-SR-09). The history records no criticism of the generic dimensions. The paper calls some subjectivity in framing analysis unavoidable, but it presents much of the disagreement as valid differences in interpretation, not as a weakness (A4-SR-09). SemEval-2023 makes the task multi-label and multilingual and reports raw agreement of α = 0.342 (A4-SR-10). It does not say which criticism led to the change. History: [frame-measurement.json](histories/frame-measurement.json).

### 3.7 Text reuse class

METER sorts stories by journalists' judgement into wholly, partially, and non-derived (A4-SR-01). PAN-PC-10 criticises METER as unfit for plagiarism detection and models reuse as graded obfuscation (A4-SR-02). No record criticises PAN in a way that led to the next news step. Boumans et al. measure agency dependence by text comparison. They grant that a shared press release "cannot be ruled out entirely" as the common source (A4-SR-04). History: [text-reuse-class.json](histories/text-reuse-class.json).

### 3.8 Link direction and storage

The steps run from Bush's two-sided link (A1-SR-01) through Nelson's two-way external link (A1-SR-03), Engelbart's directed typed link (A1-SR-02), Dexter's stored link (A1-SR-04), and the one-way Web link (A1-SR-07) to computed backlinks in Obsidian (A1-SR-09). Nelson's step carries 1960, the date he gives for a design he calls "currently undocumented" (A1-SR-03). The check counts that anchor as primary, although A1-SR-03 is secondary for the dated Xanadu designs. The Dexter criticism is aimed at the variety of existing systems, among them Engelbart's Augment, not at the 1962 report itself (A1-SR-04). Nelson's 1999 criticism of the Web link changed no recorded standard (A1-SR-03). No note tool cites a criticism as its reason (A1-SR-09, A1-SR-10). History: [link-direction.json](histories/link-direction.json).

### 3.9 Check-worthy claim

ClaimBuster ties check-worthiness to public interest (A2-SR-02). CheckThat! 2018 copies one fact-checker's choices and names ClaimBuster's lack of such a model as the contrast (A2-SR-04). Full Fact removes importance and labels only checkability, with moderate agreement, α = 0.46 (A2-SR-05). That agreement figure is Full Fact's own result, not an outside criticism. CheckThat! 2020 splits the label into an objective and a subjective question. A2-SR-08 names "the subjective nature of check-worthiness" as the reason. The history does not mark that criticism as `drove_next`, because the Full Fact step lies between the two CheckThat! steps. The 2022 survey still calls check-worthiness subjective and dependent on time (A2-SR-11). The editions from 2022 to 2025 were not read. History: [check-worthy-claim.json](histories/check-worthy-claim.json).

### 3.10 Frame

Goffman's frame is a schema a person uses to interpret events. It reaches the report through two secondary sources (A4-SR-05, A4-SR-06). Entman criticises the casual use of the term and defines framing as selection and salience in a text (A4-SR-07). A4-SR-08 reports calls to move away from studying emphasis frames and cites Cacciatore, Scheufele and Iyengar (2016) and Scheufele and Iyengar (2012) for them. The record does not show who introduced the split into equivalence and emphasis frames. It also reports that later authors argue for keeping both (A4-SR-08). The 2016 step carries the record's relevant event date. The step for the 2018 works carries the record's own date, 2025, because the record gives no date of their own. Scheufele (1999) and D'Angelo (2002) were not reached. History: [frame.json](histories/frame.json).

### 3.11 Concepts below the entry rule

- **Claim provenance.** Fact-checking as verification leaves out who first made a claim (A2-SR-01, A4-SR-15). The provenance graph adds that question (A4-SR-15). The record does not show that A4-SR-15 cites Vlachos and Riedel, so the link from that criticism to the provenance graph is the history author's reading. The detection of earlier fact-checked claims runs beside it rather than replacing it, so it is not a step (A4-SR-16). The follow-up paper Politi-Prov was not read.
- **Information change in an altered claim.** Hand coding of claim strength (A4-SR-14) is followed by a learned score of information change (A4-SR-13). The score has no direction of change. That is this survey's reading of A4-SR-13, not a recorded criticism.
- **Language-model fact-checking.** A closed-book masked model (A2-SR-09) is followed by agents with web retrieval (A2-SR-13). The 2024 shared-task step rests on a partial reading inside A2-SR-12 and has no date of its own in the record, so it is not a step.
- **The decision-detection task.** One flat class of decision dialogue acts (A3-SR-19) gives way to issue, resolution, and agreement roles (A3-SR-21). The action-item task has the same shape (A3-SR-20), but its first step is known only through A3-SR-20, so it has no history file.
- **The disentanglement task.** Utterance clustering (A3-SR-15) gives way to reply graphs (A3-SR-16). Kummerfeld et al. criticise the small size of earlier datasets. That criticism leads to their larger corpus, not to the reply graph, so the history does not mark it as `drove_next` (A3-SR-16). The earlier speaker clustering is known only through its critic (A3-SR-15).
- **Fact-checking as a verification task.** The steps are a truth value in context (A2-SR-01), synthetic Wikipedia claims (A2-SR-03), and real claims with dated evidence (A2-SR-12). The FEVER bias is a second recorded criticism (A2-SR-06). The history holds one criticism per step, so it records the one AVeriTeC names as its reason (A2-SR-12).
- **The diarization metric.** The first two steps come from DIHARD II's account and carry its date (A3-SR-22). Why the collar was introduced is not recorded.
- **SECI model.** The 1991, 1994, and 1995 texts were not read. The two read formulations are the 2000 paper (A1-SR-12) and the 2009 reply, abstract only (A1-SR-13).

The area indexes list further sequences that have no history file. These are the email threading algorithm, XMPP threads, the fact-checking pipeline, claim matching, fact-check markup, retraction records, and meeting summaries. In each, a step lacks a date of its own or a quote the check can anchor.

## 4. The reuse classes

A wire report and fifty outlets that reuse it are 51 sources. The wire report is the primary source of the factual claim. Each outlet is a source of what it did with the report. The literature gives each class a different unit: a document or word sequence for verbatim and altered reuse, one article for frames, a text and a target for stance, and a graph edge for provenance.

### 4.1 Verbatim

**Definition.** METER calls text verbatim when it appears "word-for-word to express the same information". A story is wholly derived when all its text comes from agency copy (A4-SR-01). The provenance graph labels the edge "identical, when a source quotes a statement from another source" (A4-SR-15).

**Methods.** METER uses n-gram overlap and Greedy String Tiling (A4-SR-01). Boumans et al. link articles to agency copy by cosine similarity and score near-identity with a Levenshtein-based churnalism index (A4-SR-04). Memetracker clusters quoted phrases within an edit distance of one word or a shared run of words (A4-SR-03). Fact-checking tools match "copy and paste" repeats to an existing fact-check (A4-SR-16).

**What they show and do not show.** They show that two texts share wording, and at what share. PAN calls verbatim copies easy to detect (A4-SR-02). They do not show who copied from whom: Memetracker does not identify the copying outlet (A4-SR-03). METER and Boumans et al. compare newspapers with agency copy, so their study design sets the direction; their records do not test it (A4-SR-01, A4-SR-04). A shared upstream source, such as a press release, produces the same overlap (A4-SR-04). Boumans et al. set their thresholds by manual inspection without a reported precision figure (A4-SR-04).

**Gaps.** Direction of copying and the shared-source case.

### 4.2 Altered

**Definition.** METER's "rewrite" is text "paraphrased to create a different surface appearance, but express the same information". A partially derived story mixes agency copy with other sources (A4-SR-01). The provenance graph has "paraphrased" and "textually entailed" edges (A4-SR-15). Sumner et al. treat a change of causal claim strength as alteration (A4-SR-14).

**Methods.** PAN-PC-10 models alteration as graded obfuscation (A4-SR-02). Memetracker groups the variants of quoted phrases that mutate as they spread (A4-SR-03). Sumner et al. code claim strength by hand on a seven-point scale from correlational to unconditionally causal (A4-SR-14). SPICED trains models on a five-point score of information change between a finding and its retellings (A4-SR-13). The provenance graph labels paraphrased and entailed edges between statements from retrieved articles with a textual entailment model (A4-SR-15).

**What they show and do not show.** Surface methods show changed wording, but PAN finds that kinds of reuse "do not differ very much under n-gram models" (A4-SR-02). METER's classifier confuses the partially derived class with both other classes (A4-SR-01). Sumner's scale shows the direction of change but is manual and covers health science (A4-SR-14). SPICED is automatic but has no direction, and covers science findings only (A4-SR-13). The entailment labels are automatic but carry no direction of claim strength. The record gives no accuracy figure, and the authors call the problem unsolved (A4-SR-15). Neither Sumner's scale nor SPICED shows that the outlet used the source directly (A4-SR-13, A4-SR-14).

**Gaps.** No recorded method combines an automatic score with the direction of change. Outside science, the only recorded automatic method at the level of meaning is the entailment labelling (A4-SR-15). METER and Memetracker cover news at the level of wording (A4-SR-01, A4-SR-03).

### 4.3 Reframed

**Definition.** No record defines reframing between a source and its reuse by another outlet. The nearest definitions are of a frame in one text, as selection and salience (A4-SR-07). The provenance graph's "contradicted" edge applies "when the derived statement has an opposite opinion" (A4-SR-15). MediaSpin treats spin as one of 13 bias types that an edit can add to or remove from a headline (A4-SR-17).

**Methods.** Frame labels per article use the Media Frames Corpus dimensions (A4-SR-09) or the SemEval-2023 multi-label task (A4-SR-10). Stance towards a target uses SemEval-2016 (A4-SR-11). Stance of an article towards a headline uses FNC-1 (A4-SR-12). MediaSpin labels pairs of an original and an edited headline from the same article. GPT-3.5-turbo marks each bias type as added, removed, or not relevant, and two co-authors checked 509 sampled labels (A4-SR-17). For sentiment, A4-SR-11 shows that stance and sentiment differ, so a sentiment shift alone does not show a stance shift.

**What they show and do not show.** The frame and stance methods label one text, or one text against a target. A pairwise change across outlets could be derived by labelling both texts and comparing. No record tests that comparison. MediaSpin shows that a pairwise label with a direction works for edits within one outlet. It reports inter-annotator agreement of κ = 0.67 without saying whom it compares. The most common error was the direction of the change (A4-SR-17). It does not show a frame change between a source and another outlet's version. It compares headlines only, not article bodies, and it uses no frame scheme such as the Media Frames Corpus (A4-SR-17). Agreement also bounds the single-text labels: α = 0.342 before consolidation for frames (A4-SR-10), and κ = .218 among the three related stance classes (A4-SR-12). The Media Frames Corpus treats part of the disagreement as valid differences in interpretation (A4-SR-09).

**Gaps.** This survey found no task that detects a frame change between a primary report and another outlet's version. The nearest record covers edits of one headline within one outlet (A4-SR-17). NewsEdits, which supplies MediaSpin's headline pairs, was not recorded. Newsalyze (Hamborg 2023), cited in A4-SR-17 for cross-outlet variation in sentiment and frame-bearing words, is an unread lead. No recorded task detects a sentiment shift between versions of a claim.

### 4.4 Independent

**Definition.** METER's non-derived class applies when the journalist "is confident the news agency has not been used", although words may still co-occur (A4-SR-01). In the provenance graph, source nodes without incoming edges are "prov-sources" (A4-SR-15).

**Methods.** METER's classifier assigns the non-derived class among the three. The record gives only a best ternary F1 of 0.664 and no figure for the partially derived class, which the classifier confuses with both others (A4-SR-01). The provenance graph treats the absence of a found edge as independence (A4-SR-15).

**What they show and do not show.** Both show the absence of detected reuse. Neither shows independence. Influence by "another uncited source" is left for future work (A4-SR-15). Boumans et al. cannot rule out a shared press release (A4-SR-04). Sumner et al. cannot tell whether journalists read the press release or the paper (A4-SR-14).

**Gaps.** No recorded method separates independent reporting from undisclosed reuse of a shared upstream source (A4-SR-04, A4-SR-14, A4-SR-15). Spread and reach are tracked only by Memetracker, which reports a typical lag of 2.5 hours between news and blog peaks (A4-SR-03). No record measures reach per outlet. The search plan did not cover reach per outlet, so this gap reflects the search, not the literature.

## 5. What this means for the wider knowledge system

This section is interpretation. Each point names the findings it rests on. None of it has been tested.

**Claims, ideas, and decisions as distinct units.** The literature treats claims and decisions separately and gives each its own detector. Claims have detection and matching (A2-SR-07, A2-SR-08, A2-SR-10). Decisions and action items are role structures spread over several utterances (A3-SR-20, A3-SR-21). So the system should store a decision as an issue, a proposal, and an agreement, each anchored to utterances, not as one sentence. The flat formulations reached F-scores of about 0.3 and 0.35 (A3-SR-20, A3-SR-21). No record in this survey treats an idea as a unit of its own.

**Message identity and threading as provenance anchors.** Every source type offers an identifier, with different scope. A Message-ID is global by rule but defective in practice (A3-SR-05, A3-SR-06). A Slack `ts` is unique only within a channel (A3-SR-14). An XMPP stanza ID is unique only within the assigning entity (A3-SR-10). A Matrix event ID is a content hash (A3-SR-11). So an anchor must store the identifier together with its scope. An import must tolerate missing and contradictory parents (A3-SR-06, A3-SR-07). A Slack export without thread fields loses structure (A3-SR-13). The Matrix history suggests a hash of the imported item as a scope-free ID (A3-SR-11).

**The propagation edges, and which a script can check.** The provenance graph's labels map onto the stakeholder's classes: identical, paraphrased or entailed, contradicted, and no edge (A4-SR-15). A script can check a verbatim edge by overlap (A4-SR-01, A4-SR-04). A script can score an altered edge, but without direction (A4-SR-13). A reframed edge rests on labels with low agreement (A4-SR-10, A4-SR-12), so it should be stored as an attributed judgement. The one recorded pairwise label works within one outlet and errs most often on direction (A4-SR-17), so a script's reframing label also needs a person's review. An independent edge cannot be checked from text (A4-SR-04, A4-SR-15). The system should record it as "no reuse found", and only a person or a disclosed source turns it into independence. Repetition adds no support: claim matching groups mentions (A2-SR-10), and a group raises a mention count only.

**Time.** Three findings make time part of the record. AVeriTeC allows only evidence published before the claim (A2-SR-12). Check-worthiness changes over time (A2-SR-11). The W3C State records the target version an annotation meant (A1-SR-18). So every anchor needs the source's own timestamp and the version it read. Slack's `ts` holds a time but is an identifier (A3-SR-14), so the import must not treat it as a clock alone.

**Where the factory's method carries over.** Quoted anchors match the W3C Text Quote Selector (A1-SR-18), and the position selector's brittleness argues for quotes over offsets. CREC carries a retraction status to every place the item appears (A2-SR-20), so a correction to a source record should reach every claim that cites it. Deterministic checks fit identifiers, threading, and verbatim overlap (A3-SR-07, A4-SR-04). Human decisions fit independence (A4-SR-15), frames (A4-SR-09), and meeting decisions (A3-SR-20, A3-SR-21). The SECI critics support storing messages as information with a known speaker, not as captured knowledge (A1-SR-14).

## 6. Structured block

```json
{
  "findings": [
    {
      "title": "Link models trade direction against storage, and few record link provenance",
      "summary": "Hypertext moved from two-sided and two-way links (Bush, Nelson) through Dexter's stored link component to the Web's one-way embedded link. Current note tools compute backlinks inside one vault, and their documentation records no author or date for a link. The W3C Web Annotation Data Model is the recorded form that stores creator, creation time, a quote selector, and the target version on a separate annotation resource.",
      "source_record_refs": ["A1-SR-01", "A1-SR-02", "A1-SR-03", "A1-SR-04", "A1-SR-05", "A1-SR-07", "A1-SR-09", "A1-SR-10", "A1-SR-17", "A1-SR-18"]
    },
    {
      "title": "Enterprise knowledge management is contested at its base",
      "summary": "The SECI model describes conversion between tacit and explicit knowledge. Critics argue that tacit knowledge cannot be captured, that knowledge management manages information or work practices, that the term tacit knowledge has at least eight uses, and that the conversion modes lack evidence. The proponents' 2009 reply was read as an abstract only.",
      "source_record_refs": ["A1-SR-12", "A1-SR-13", "A1-SR-14", "A1-SR-15", "A1-SR-16"]
    },
    {
      "title": "Fact-checking runs as a pipeline with claim matching as its own step",
      "summary": "A 2022 survey names claim detection, evidence retrieval, and verification with verdict and justification. CheckThat! adds a check against previously fact-checked claims. Claim matching widened from ranking verified claims to pairs of messages served by one fact-check, in five languages.",
      "source_record_refs": ["A2-SR-04", "A2-SR-07", "A2-SR-08", "A2-SR-10", "A2-SR-11"]
    },
    {
      "title": "Verification moved to real claims with dated evidence, and retrieval helps language models",
      "summary": "FEVER's synthetic claims let a claim-only model predict labels. AVeriTeC uses real claims and restricts evidence to documents published before the claim. Closed-book language-model checking stayed below retrieval systems in 2020, and agents with web search did better than the same models without it in a 2024 study, with uneven accuracy.",
      "source_record_refs": ["A2-SR-03", "A2-SR-06", "A2-SR-09", "A2-SR-12", "A2-SR-13"]
    },
    {
      "title": "Verdicts have markup; corrections have little",
      "summary": "ClaimReview records a claim summary, the reviewed item, and a rating, and a Claim can carry its appearances and first appearance, with no relation types between claims. Ratings are not standard. Google Search is phasing out ClaimReview display. News corrections have one schema.org property without kind or severity; scholarly retractions have NISO CREC, which excludes corrections.",
      "source_record_refs": ["A2-SR-14", "A2-SR-15", "A2-SR-16", "A2-SR-17", "A2-SR-18", "A2-SR-19", "A2-SR-20"]
    },
    {
      "title": "Email identity and threading rules are explicit but unreliable in practice",
      "summary": "Message-ID must be globally unique per message version, and References is built from the parent's References plus the parent's Message-ID. Header surveys and the IMAP threading standard document free text, contradictory References, and unused multi-parent forms, so threading code must tolerate them. Without usable References, the IMAP algorithm takes the first valid Message-ID in In-Reply-To as the parent.",
      "source_record_refs": ["A3-SR-02", "A3-SR-03", "A3-SR-04", "A3-SR-05", "A3-SR-06", "A3-SR-07"]
    },
    {
      "title": "Chat identifiers differ in scope",
      "summary": "XMPP separates thread identity from message identity, and its stable stanza ID is Experimental and scoped to the assigning entity. Matrix derives event IDs from a hash of the event and keeps threads flat. Slack identifies a message by channel plus ts, and its official export does not document thread fields.",
      "source_record_refs": ["A3-SR-08", "A3-SR-09", "A3-SR-10", "A3-SR-11", "A3-SR-12", "A3-SR-13", "A3-SR-14"]
    },
    {
      "title": "Conversation structure, speakers, and meeting outcomes are role and graph tasks",
      "summary": "Disentanglement now labels reply graphs and takes connected components as conversations. Diarization labels anonymous speakers and moved to full DER plus JER. Decision and action-item detection label the roles of utterances instead of one flat class. QMSum restates meeting summarization as answers to queries.",
      "source_record_refs": ["A3-SR-15", "A3-SR-16", "A3-SR-17", "A3-SR-18", "A3-SR-19", "A3-SR-20", "A3-SR-21", "A3-SR-22"]
    },
    {
      "title": "Verbatim reuse is detectable by text overlap",
      "summary": "METER, the churnalism index, Memetracker, and fact-checking repeat matching detect verbatim and lightly edited reuse. Memetracker does not show which outlet copied from which. METER and Boumans et al. compare newspapers with agency copy, so their study design sets the direction and does not test it. A shared press release produces the same overlap.",
      "source_record_refs": ["A4-SR-01", "A4-SR-02", "A4-SR-03", "A4-SR-04", "A4-SR-15", "A4-SR-16"]
    },
    {
      "title": "Altered meaning has a manual method with a direction of change and automatic methods without one",
      "summary": "Sumner et al. code causal claim strength by hand on an ordered scale. SPICED scores information change in science findings automatically, without a direction. The provenance graph labels paraphrased and entailed edges between statements from retrieved articles with a textual entailment model; the record gives no accuracy figure, and the authors state that the problem is not solved. Surface methods separate kinds of reuse poorly.",
      "source_record_refs": ["A4-SR-01", "A4-SR-02", "A4-SR-13", "A4-SR-14", "A4-SR-15"]
    },
    {
      "title": "Reframing is measured per text or within one outlet, not between a source and another outlet's reuse",
      "summary": "Frame and stance methods label one article or one text against a target, with low human agreement on the finer classes. MediaSpin labels spin and 12 other bias types as added or removed between two versions of one headline from the same outlet, with LLM labels whose most common error is the direction. This survey found no recorded source that defines or detects a frame change between a primary report and another outlet's version. Stance and sentiment are separate signals.",
      "source_record_refs": ["A4-SR-07", "A4-SR-09", "A4-SR-10", "A4-SR-11", "A4-SR-12", "A4-SR-15", "A4-SR-17"]
    },
    {
      "title": "Independent reporting cannot be separated from undisclosed shared-source reuse",
      "summary": "METER's non-derived class and the provenance graph's source nodes mark the absence of detected reuse. Three records name the limit that an uncited shared source cannot be ruled out. The provenance graph's authors state that claim provenance is not solved.",
      "source_record_refs": ["A4-SR-01", "A4-SR-04", "A4-SR-14", "A4-SR-15"]
    },
    {
      "title": "Ten concepts meet the entry rule of concept-history-check",
      "summary": "In-Reply-To and References, the Matrix event ID, the stance-detection task, the Message-ID rule, Information about a link and the annotation model, Measuring a frame in text, Text reuse class, Link direction and storage, Check-worthy claim, and Frame meet the rule, in the order the check computes. Eight more concepts have histories below the rule.",
      "source_record_refs": ["A1-SR-01", "A1-SR-02", "A1-SR-03", "A1-SR-04", "A1-SR-06", "A1-SR-07", "A1-SR-09", "A1-SR-18", "A2-SR-02", "A2-SR-04", "A2-SR-05", "A2-SR-08", "A2-SR-11", "A3-SR-01", "A3-SR-02", "A3-SR-03", "A3-SR-04", "A3-SR-05", "A3-SR-06", "A3-SR-07", "A3-SR-11", "A4-SR-01", "A4-SR-02", "A4-SR-04", "A4-SR-06", "A4-SR-07", "A4-SR-08", "A4-SR-09", "A4-SR-10", "A4-SR-11", "A4-SR-12"]
    }
  ],
  "uncertainties": [
    "Matrix event ID: all three steps come from one record and carry its publication date, which the record set from memory and marks for checking (A3-SR-11).",
    "Frame: the 2016 step reaches the report through a 2025 secondary source and carries its relevant event date, and the step for the 2018 works carries the record's 2025 date (A4-SR-08); Goffman reaches it through two secondary sources (A4-SR-05, A4-SR-06).",
    "The stance-detection task: the FNC-1 definition is known only through Hanselowski et al. (A4-SR-12), which the check counts as primary because the record is primary for its own reanalysis.",
    "Measuring a frame in text: the issue-specific codebook step is known only through its critic (A4-SR-09).",
    "Link direction: Nelson's 1960 date is his own account of an undocumented design (A1-SR-03), which the check counts as primary, and the Dexter criticism addresses existing systems in general (A1-SR-04).",
    "In-Reply-To and References: A3-SR-04 did not record the obsolete syntax of RFC 2822, so the records do not show whether the RFC 5322 rule for phrases is new (A3-SR-04, A3-SR-05).",
    "Message-ID: the link from the RFC 5256 criticism to the RFC 5322 change is an inference; RFC 5322 gives no reason (A3-SR-05, A3-SR-07).",
    "The JWZ header survey is one developer's archive with no stated method (A3-SR-06).",
    "Agreement figures on frames and stance are low (A4-SR-10, A4-SR-12), so labels from these schemes are uncertain in themselves.",
    "MediaSpin labels come from one LLM, checked against two co-authors on 509 sampled labels; the most common error is the direction of the change (A4-SR-17)."
  ],
  "evidence_gaps": [
    "This survey found no method that detects a frame change between a primary report and another outlet's version. The nearest record, MediaSpin, covers bias added or removed between two versions of one headline within one outlet (A4-SR-17). NewsEdits, its source of headline pairs, was not recorded. Newsalyze (Hamborg 2023), which A4-SR-17 cites for cross-outlet variation in sentiment and frame-bearing words, is an unread lead.",
    "No recorded method separates independent reporting from undisclosed reuse of a shared upstream source.",
    "No recorded task detects a sentiment shift between versions of a claim.",
    "No recorded method combines an automatic score of altered meaning with its direction.",
    "No record measures reach per outlet, and the search plan did not cover it; Memetracker gives only attention lags.",
    "No record shows a machine-readable correction to a fact-check.",
    "No record covers the step from anonymous diarization labels to named speakers.",
    "Chat export formats other than Slack were not searched.",
    "No recorded tool documentation names the Zettelkasten or the Memex as the model for its backlinks.",
    "CheckThat! editions from 2022 to 2025 and the Politi-Prov provenance paper were not read."
  ],
  "limitations": [
    "Several sources are abstract-only: A1-SR-13 and A1-SR-15.",
    "Several steps rest on secondary records: A1-SR-05, A1-SR-08, A1-SR-11 for Malone, A4-SR-05, A4-SR-06, A4-SR-08, A4-SR-16, and A2-SR-11 for the works it surveys.",
    "Four records count as primary but are secondary for an earlier formulation they describe: A1-SR-03, A3-SR-22, A4-SR-09, and A4-SR-12.",
    "Unreachable sources include Nonaka 1994, Gourlay 2006 full text, Nonaka and von Krogh 2009 full text, Goffman 1974, Cacciatore et al. 2016, Scheufele 1999, the COPE retraction guidelines, the ICSI corpus paper, and the Open Annotation drafts.",
    "A4-SR-17 was read from arXiv v3, not from the ICWSM proceedings, and only spot-checked against v5.",
    "Tool and vendor documentation states features, not use or adoption (A1-SR-09, A1-SR-10, A2-SR-15, A3-SR-13, A3-SR-14).",
    "Copyright and data protection were out of scope; every source counts as storable."
  ],
  "candidates_for_deeper_falsification_study": [
    "A script can record a verbatim reuse edge from a downstream item to a wire report by text overlap alone, without human review. Refuted if a hand-checked sample shows more false verbatim edges than a threshold set before the test, for example pairs that share only a press release (A4-SR-04).",
    "Two annotators can label outlet-to-wire pairs with the four reuse classes at useful agreement. Refuted if their agreement falls below a kappa set before the test, as the related stance classes did at .218 (A4-SR-12).",
    "Independent reporting cannot be established from text alone, so the system records only 'no reuse found' until a person or a disclosed source decides. Refuted if a text-only method separates independent reports from undisclosed shared-source reuse on a labelled sample (A4-SR-04, A4-SR-15).",
    "Email threads can be rebuilt from Message-ID, In-Reply-To, and References alone for the system's own mailboxes. Refuted if more replies than a set share lack a resolvable parent or carry contradictory References (A3-SR-06, A3-SR-07).",
    "A hash of the imported item serves as a scope-free identifier across email, chat, and transcripts. Refuted if two distinct imported items get the same identifier, or one item imported twice gets two (A3-SR-11).",
    "Decisions in meeting and session transcripts can be extracted as issue, proposal, and agreement, each anchored to an existing utterance. Refuted if, on a transcript with a known decision list, extraction misses decisions a person lists or anchors one to an utterance that does not exist (A3-SR-21).",
    "Claim matching groups the mentions of one claim across sources stably enough to keep a mention count. Refuted if two runs or two annotators group the same mentions differently beyond a set share (A2-SR-10).",
    "A frame label on an item is too unreliable to store as a fact and must be stored as an attributed judgement. Refuted if annotators on the system's own items reach alpha 0.667 or higher (A4-SR-10).",
    "Ordering a claim's mentions by the source's own timestamp agrees with their reply and reuse edges. Refuted if a sample shows a downstream item dated before its source (A2-SR-12, A3-SR-14)."
  ]
}
```

## 7. Uncertainties, evidence gaps, and limitations

**Unreachable sources.** Several primary sources could not be read. These are Nonaka 1994 (TLS failure), the full texts of Gourlay 2006 and of Nonaka and von Krogh 2009, Goffman 1974, and Cacciatore et al. 2016. The COPE retraction guidelines, the ICSI corpus paper, and the Open Annotation drafts were also out of reach. Each gap is listed in its area index. Where a record stands in, it is marked secondary or abstract-only.

**Abstract-only records.** A1-SR-13 and A1-SR-15 rest on abstracts. So the SECI debate in this report shows that criticism and a reply exist, not what the reply answers.

**Secondary steps.** Goffman's frame (A4-SR-05, A4-SR-06), the 2016 and 2018 framing steps (A4-SR-08), the FNC-1 definition (A4-SR-12), the early diarization metrics (A3-SR-22), issue-specific frame codebooks (A4-SR-09), and Nelson's 1960 design (A1-SR-03) reach the report second-hand. The check counts A1-SR-03, A3-SR-22, A4-SR-09, and A4-SR-12 as primary, because each is primary for its own work. Their rank in section 3 should be read with that in mind.

**Evidence gaps that matter most.** This survey found no method for pairwise reframing across outlets and none for separating independent from shared-source reporting. For reframing, the nearest record is MediaSpin, which labels bias added or removed between two versions of one headline within one outlet (A4-SR-17). It was read from arXiv v3, its labels come from one LLM, and NewsEdits, its source of headline pairs, was not recorded. Newsalyze, cited in A4-SR-17, is an unread lead. Sentiment shift between versions and machine-readable corrections to fact-checks have no recorded method either. Reach per outlet has none, but the search plan did not cover it. Section 4 names each gap in place.

**Scope and freshness.** The records were retrieved on 2026-11-18. Vendor documentation states features, not use. Language-model and fact-checking work from 2022 onwards is thin: the CheckThat! editions from 2022 to 2025 and the full 2024 AVeriTeC overview were not read.
