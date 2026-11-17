# A3-SR-01 — The Open Provenance Model Core Specification (v1.1)

```json
{
  "source_identity": "Moreau, L. (ed.) et al., 'The Open Provenance Model Core Specification (v1.1)', Future Generation Computer Systems 27(6), 743-756, DOI 10.1016/j.future.2010.07.005; preprint dated 27 July 2010",
  "author_or_issuing_body": "Luc Moreau (editor) with Ben Clifford, Juliana Freire, Joe Futrelle, Yolanda Gil, Paul Groth, Natalia Kwasnikowska, Simon Miles, Paolo Missier, Jim Myers, Beth Plale, Yogesh Simmhan, Eric Stephan, Jan Van den Bussche",
  "publisher": "Elsevier (journal); the copy read is hosted on Yolanda Gil's project site, knowledgecaptureanddiscovery.github.io",
  "publication_date": "2011-06-01T00:00:00Z",
  "relevant_event_date": "2007-08-01",
  "source_family": "Primary. Specification paper by the designers of the Open Provenance Model, a lineage that starts with the Provenance Challenge series (2006 to 2010). Several authors (Moreau, Groth, Gil, Missier, Miles) also wrote the later W3C Provenance Incubator report and PROV documents, so those sources are not independent of this one.",
  "precise_evidence_location": "Abstract; Section 1 (history paragraphs on the first, second and third Provenance Challenge and on versions 1.00, 1.01, 1.1); Section 10 'Discussion, Related and Future Work'.",
  "method": "The authors specify the model and describe the community process that produced it. The text gives no empirical evaluation beyond the report that fourteen teams exchanged provenance in the third challenge.",
  "limitations": "Publication date is month-only (June 2011); the first day is used. Relevant event date is the August 2007 workshop at which version 1.00 was crafted, month-only. The paper reports the authors' own view of their model: 'OPM is the first model to be purely technology agnostic' is a self-assessment. The text does not say why W3C later replaced OPM with PROV and does not mention the W3C Provenance Working Group. A one-line mention of the Incubator group's planned mapping to OPM is the only link to later work.",
  "provenance": "Fetched 2026-11-17 with curl from https://knowledgecaptureanddiscovery.github.io/yolanda_gil_website/papers/moreau-etal-fgcs11.pdf and converted with pdftotext. Quotes below are exact and were checked against the extracted text. Re-verify by running the same two commands, or open the ScienceDirect page for the journal version (S0167739X10001275)."
}
```

## Evidence

Quotes are exact. Section numbers follow the paper.

- Abstract, requirement 1: "To allow provenance information to be exchanged between systems, by means of a compatibility layer based on a shared provenance model."
- Section 1: "The first Provenance Challenge was followed by the second Provenance Challenge, aiming at establishing interoperability of systems, by exchanging provenance information. Thirteen teams [7] responded to this second challenge. Discussions indicated that there was substantial agreement on a core representation of provenance. As a result, following a workshop in Salt Lake City, in August 2007, a data model was crafted and released as the Open Provenance Model (v1.00) [8]."
- Section 1: "In June 2008, twenty participants attended the first OPM workshop [10] to discuss the OPM specification v1.00." The workshop led to version 1.01, "actively used during the Third Provenance Challenge". The third-challenge teams "decided to adopt an open-source model for the governance[13] of OPM." Proposals were "publicly reviewed, and put to vote [14]; the result of which is version 1.1".
- Section 1: "a provenance graph is defined to be a record of a past execution (or current execution), and not a description of something that could happen in the future."
- Section 10, open gap on agents: "Since the Third Provenance Challenge did not test agents much, further guidance is needed on how best to describe systems in the presence of agents."
- Section 10, open gap on collections: "However, no guidance is provided by OPM to express such collections and their relation to their constituents."
- Section 10, relation to later work: "The W3C Incubator on Provenance [24] has identified use cases and requirements for provenance on the Web, and is proposing a mapping of the above models of provenance to OPM."

## What the source shows

The record shows the dated sequence from the 2006 workshop to Open Provenance Model version 1.1, and two gaps the authors name themselves (agents, collections).

## What the source does not show

It does not show who criticised the model after 2010 or why a W3C standard followed. It gives no adoption figures beyond the third challenge.

## Failed searches and gaps

The openprovenance.org page dates version 1.00 to December 2007, but this record uses only the paper's own wording (August 2007 workshop). The two dates are not reconciled.
