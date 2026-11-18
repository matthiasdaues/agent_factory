# Area 2: Claims Across News

This index covers assignment A2 of the survey plan. It lists 20 source records
in [area-2/](area-2/), numbered A2-SR-01 to A2-SR-20. Each record holds the
source's own words in its Evidence section. The index reports what the sources
document; it does not judge whether a concept holds.

## State of the Art

Research splits automated fact-checking into a pipeline. A survey of 2022 names
three stages: claim detection, evidence retrieval, and claim verification. It
splits verification into a verdict and a justification (A2-SR-11). The CheckThat!
lab adds a step between detection and retrieval: a check whether the claim was
fact-checked before (A2-SR-07, A2-SR-08).

Claim detection starts with ClaimBuster. It sorts sentences into three classes
and calls a factual claim check-worthy when the general public would want to
know whether it is true (A2-SR-02). Full Fact rejects the importance judgement
and labels only whether a claim can be checked (A2-SR-05). CheckThat! first
copied one fact-checker's choices (A2-SR-04), then split the label into an
objective question and a subjective question (A2-SR-08). The 2022 survey still
calls check-worthiness subjective and dependent on time (A2-SR-11).

Claim matching ranks already fact-checked claims against a new claim (A2-SR-07).
Meedan widens it to any two messages that one fact-check can serve, in five
languages (A2-SR-10).

Verification datasets moved from synthetic claims to real ones. FEVER builds
claims by altering Wikipedia sentences (A2-SR-03). A claim-only model predicts
its labels well without evidence (A2-SR-06). AVeriTeC takes real claims from 50
fact-checkers and allows only evidence published before the claim (A2-SR-12).

Language-model fact-checking began in 2020 as a closed-book test on FEVER. It
stayed below systems with retrieval (A2-SR-09). In a 2024 study, GPT-4 agents
with web search did better than the same models without it. Their accuracy
varied by language and verdict (A2-SR-13). In the 2024 AVeriTeC shared task,
most systems used a language model to generate search questions (A2-SR-12, note).

Fact-checkers publish their verdicts as schema.org ClaimReview markup. A record
holds a summary of the claim, the reviewed item, and a rating (A2-SR-14). A
Claim can carry its appearances and its first appearance (A2-SR-14). Ratings
differ between fact-checkers, and Google asks each publisher to document its
scale (A2-SR-15). The Duke Reporters' Lab counts 136,744 tagged articles from
177 organisations (A2-SR-17). Google Search is phasing out ClaimReview display;
Fact Check Explorer keeps it (A2-SR-15). AVeriTeC draws its claims from the
ClaimReview-based Google API (A2-SR-12). MediaReview records fact-checks of
images and video, with a link to the original media (A2-SR-16, A2-SR-17).

Fact-checkers commit to a public corrections policy under the IFCN Code of
Principles (A2-SR-18). News articles can point to a correction through the
schema.org `correction` property (A2-SR-19). Scholarly retractions have a
detailed metadata practice in NISO CREC, which leaves corrections and errata
out of scope (A2-SR-20). No source in this area records a correction to a fact-check
in machine-readable form.

## Hardened Concepts

### Check-worthy claim

1. **Public interest, three classes** (October 2015). A check-worthy factual
   sentence is one the general public wants to know is true or false (A2-SR-02).
   Criticism: the label mixes a checkable claim with an editorial judgement of
   importance, and a ranking needs a cut-off score (A2-SR-05). CheckThat! adds
   that ClaimBuster copies no real fact-checker's choices (A2-SR-04).
2. **One fact-checker's selection, as a ranking** (August 2018). Systems rank
   debate sentences by the choices of FactCheck.org (A2-SR-04). Criticism: the
   lab's own 2020 overview names "the subjective nature of check-worthiness"
   for tweets (A2-SR-08).
3. **Checkable claim, importance removed** (September 2018, in parallel with
   step 2). Full Fact labels whether a sentence holds a claim that can be checked
   and leaves importance to fact-checkers (A2-SR-05). Criticism: agreement on
   the seven categories is moderate, alpha 0.46 (A2-SR-05). No source was found
   that criticises the binary schema from outside.
4. **Objective and subjective questions** (July 2020). Annotators answer
   whether a tweet holds a verifiable factual claim, then whether a
   fact-checker should verify it; both must be yes (A2-SR-08). Criticism:
   check-worthiness stays subjective and changes over time (A2-SR-11, 2022).
5. **Gap.** The CheckThat! editions of 2022 to 2025 were not read. Whether they
   changed the definition again is open.

### Fact-checking as a verification task

1. **Truth value for a claim in context** (June 2014). Ordinal labels; the
   analysis behind a verdict is left out (A2-SR-01). Criticism: gap. FEVER's
   stated reason for a new dataset was not recorded.
2. **Three labels against Wikipedia evidence** (June 2018). FEVER builds
   185,445 claims by altering Wikipedia sentences (A2-SR-03). Criticism: a
   claim-only model reaches 61.7% because negation marks refuted claims
   (A2-SR-06, 2019). AVeriTeC adds that purpose-made claims are unlike
   journalists' claims (A2-SR-12).
3. **Real-world claims with dated evidence** (May 2023). AVeriTeC uses claims
   from 50 fact-checkers, question-answer evidence, and evidence published
   before the claim (A2-SR-12). Criticism: none found yet.

### Claim matching against fact-checked claims

1. **Ranking verified claims for an input claim** (May 2020). The input is a
   check-worthy claim. The output ranks verified claims that help verify it
   (A2-SR-07). The task runs as CheckThat! 2020 Task 2 (A2-SR-08). Criticism:
   English and US politics only, and each claim is matched to one fact-check
   report, not to all of its earlier occurrences (A2-SR-10).
2. **Pairs of messages served by one fact-check** (June 2021). Any two
   messages qualify, in five languages (A2-SR-10). Criticism: none found yet.

### Fact-checking pipeline

1. **Detect, extract and normalise, check** (August 2018) (A2-SR-04).
   Criticism: a check against already fact-checked claims should be a step of
   its own, as Shaar et al. argue, citing Hassan et al. 2017 (A2-SR-07).
2. **Four steps with claim matching** (May to July 2020). Check-worthiness,
   matching, evidence retrieval, verification (A2-SR-07, A2-SR-08). Criticism:
   the earlier survey framework of Thorne and Vlachos (2018) lacks claim
   detection and justification production (A2-SR-11). That survey was not read.
3. **Three stages with justification** (2021 preprint, 2022 journal).
   Claim detection, evidence retrieval, verification with verdict and
   justification (A2-SR-11). Criticism: none found yet.

### Language-model fact-checking

1. **Closed-book masked language model** (July 2020). BERT predicts a masked
   token of the claim, and a match counts as support (A2-SR-09). Criticism: the
   authors state it stays below systems with knowledge bases (A2-SR-09). A
   temporal split guards test claims against leaks from pretraining data
   (A2-SR-12).
2. **Language-model agent with web retrieval** (October 2023 to February 2024).
   GPT agents search, cite, and decide; retrieval improves accuracy (A2-SR-13).
   Criticism: inconsistent accuracy across languages and verdicts (A2-SR-13).
3. **Language-model question generation in a shared task** (October 2024).
   Most systems generate questions before retrieval (A2-SR-12, note). This
   step rests on a partial reading.

### Fact-check markup

1. **ClaimReview, item reviewed as a creative work** (from 2015). The
   Reporters' Lab starts ClaimReview in 2015 (A2-SR-17). Google first
   recommended CreativeWork as the reviewed item (A2-SR-15). Criticism: gap.
   The reason for the move to Claim was not found.
2. **ClaimReview with a Claim type** (current). A Claim carries its
   appearances, its first appearance, and `sameAs` links for variants
   (A2-SR-14). Criticism: ClaimReview "proved insufficient" for images and
   video (A2-SR-17).
3. **MediaReview** (development from September 2019). It adds a rating of
   media authenticity and a link to the original (A2-SR-16, A2-SR-17).
   Criticism: the schema.org page itself calls it a work in progress; most
   entries are "Missing Context", not deepfakes (A2-SR-16, A2-SR-17).

### Recording a retraction

1. **Gap.** Earlier guidance, such as the COPE retraction guidelines of 2009
   and 2019, could not be fetched.
2. **NISO CREC metadata** (June 2024). Named metadata elements and a
   "RETRACTED:" title prefix carried to every platform (A2-SR-20). Criticism
   of earlier practice: inconsistent display, shared DOIs, deleted records
   (A2-SR-20). Criticism of CREC itself: none found.

## Gaps

- The COPE retraction guidelines returned HTTP 403 at publicationethics.org.
  CREC cites them; their text is not recorded.
- No standard was found for recording news corrections beyond the schema.org
  `correction` property and the IFCN corrections principle. The Trust Project
  documentation was not read.
- The IFCN code pages carry no date. The launch year and earlier versions of
  the code are not recorded.
- The date and reason of Google's ClaimReview phase-out are not on the
  documentation page.
- CheckThat! 2019 and 2022 to 2025 overviews were not read. CheckThat! 2021
  was read in its short form only and is not a record.
- ClaimBuster's KDD 2017 paper and the ClaimBuster dataset paper of 2020 were
  downloaded. Only the 2020 definitions are cited, inside A2-SR-02.
- The 2024 AVeriTeC shared-task overview was read in part and appears only as
  a note in A2-SR-12.
- Thorne and Vlachos (2018), the earlier survey, was not read.
- No outside criticism was found for the Full Fact binary schema, for
  AVeriTeC, or for claim matching across languages.
- Stance detection and the tracing of a claim's origin were left to area 4,
  as the brief requires.
