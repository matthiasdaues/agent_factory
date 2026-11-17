# A3-SR-06 — Groth, Gibson and Velterop, "The Anatomy of a Nano-publication" (2010)

```json
{
  "source_identity": "Groth, P., Gibson, A., Velterop, J., 'The Anatomy of a Nano-publication' (draft, v3), W3C wiki file cwa-anatomy-nanopub-v3.pdf; published version: Information Services and Use 30, 51-56, 2010, DOI 10.3233/ISU-2010-0613",
  "author_or_issuing_body": "Paul Groth (VU University Amsterdam), Andrew Gibson (University of Amsterdam), Johannes Velterop (Concept Web Alliance / NBIC)",
  "publisher": "W3C wiki (HCLS Interest Group SWAN/SIOC rhetorical-structure meeting page) for the draft read; IOS Press for the published paper",
  "publication_date": "2010-02-15T00:00:00Z",
  "relevant_event_date": "2010-02-15",
  "source_family": "Primary. First formal model of nanopublications, from the Concept Web Alliance lineage of A3-SR-05. The text read is a pre-publication draft; the IOS Press version is the same work.",
  "precise_evidence_location": "Abstract; Section 2 'Core Model' (definitions); Section 3 'A Realization as Named Graphs'; Section 5 'Attribution, Review, Citation'.",
  "method": "A design paper: the authors define a model and show how existing Semantic Web technology (Named Graphs, SWAN provenance, Semantic Web Publishing ontology) can realize it.",
  "limitations": "The date 2010-02-15 is taken from the meeting folder in the file's W3C wiki URL; the draft's own date was not printed in the extracted text. The published IOS Press text was not read (only its abstract at research.vu.nl), so differences between draft and published model are unknown. Later nanopublication documents use 'assertion, provenance, publication info' (A3-SR-10), not the 'statement, annotation, S-Evidence' terms here; this record does not show why they changed. The authors belong to the group that promoted nanopublications.",
  "provenance": "Fetched 2026-11-17 with curl from https://www.w3.org/wiki/images/c/c0/HCLSIG$$SWANSIOC$$Actions$$RhetoricalStructure$$meetings$$20100215$cwa-anatomy-nanopub-v3.pdf and converted with pdftotext. Quotes are exact and were checked against the extracted text. The abstract of the published version was read at https://research.vu.nl/en/publications/the-anatomy-of-a-nanopublication/ and matches."
}
```

## Evidence

- Section 2 definitions: "Statement – A triple that is uniquely identifiable." "Annotation – A triple such that the subject of the triple is a statement." "Nanopublication – A set of annotations that refer to the same statement and contains a minimum set of (community) agreed upon annotations." "S-Evidence – all the nanopublications that refer the same statement."
- Section 2: nanopublications "need to be citable, attributable, and reviewable" and "easily aggregated and identified across the Web".
- Section 3: "Each statement is a separate Named Graph." "Thus, the simplest nano-publication has two Named Graphs, one with a statement and another containing the annotations on that statement." The paper adds that Named Graphs "are not yet a W3C standard".
- Section 5, on attribution: "While the provenance ontology from SWAN provides a reasonable set of information describing the annotations within a nano-publication. It does not yet provide a good mechanism to for claiming the contents of a nano-publication." The authors propose the Semantic Web Publishing ontology and its `assertedBy` relationship, plus digital signatures.

## What the source shows

It shows the second formulation: a nanopublication is a set of annotations on one uniquely identified statement, realized as Named Graphs. It names one gap in an earlier tool (SWAN provenance cannot express who claims a nanopublication) and the borrowed fix.

## What the source does not show

It does not show the final published text, the later three-part structure, or any evaluation.

## Failed searches and gaps

The IOS Press full text (DOI above) was not reachable. The ACM Digital Library and academia.edu pages returned no full text.
