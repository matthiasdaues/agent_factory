# A5-SR-06: Gutierrez, Hurtado, Vaisman, Temporal RDF

```json
{
  "source_identity": "Claudio Gutierrez, Carlos Hurtado, Alejandro Vaisman, 'Temporal RDF', ESWC 2005, LNCS 3532, pp. 93-107; technical report TR/DCC-2005-002, https://www.dcc.uchile.cl/TR/2005/TR_DCC-2005-002.pdf",
  "author_or_issuing_body": "Claudio Gutierrez, Carlos Hurtado (Universidad de Chile); Alejandro Vaisman (Universidad de Buenos Aires)",
  "publisher": "Springer (conference version); Department of Computer Science, Universidad de Chile (technical report)",
  "publication_date": "2005-01-01T00:00:00Z",
  "relevant_event_date": "2005-01-01",
  "source_family": "Primary. Technical-report version of the ESWC 2005 paper. Later extended by the authors in a journal paper (not read). Cited by Hogan et al. 2021 (A5-SR-09) as the 'Temporal RDF' annotation.",
  "precise_evidence_location": "Section 1.1 Problem Statement (Versioning vs. Time Labeling; Timestamp vs. Snapshot Semantics); Section 1.3 Contributions",
  "method": "Formal proposal: a semantics, syntax and inference system for RDF graphs whose triples carry temporal labels, with a sketch of a query language. Proofs are omitted in this version.",
  "limitations": "Year only; date set to 1 January 2005 (the PDF metadata shows 2008, which is the report file date, not the paper date). The text read is the technical report, not the Springer version, so page wording may differ. Shows the proposal and its stated reasons; contains no implementation or usage data and no external criticism. Blank nodes and reification are named as open complications.",
  "provenance": "PDF downloaded with curl on 2026-11-17 and extracted with pdftotext. Re-verify at the URL above or DOI 10.1007/11431053_7."
}
```

## Evidence

- Section 1 (Introduction): "little attention has deserved the problem of representing, updating and querying temporal information in RDF."
- Section 1.1: two ways to add time: labeling (label each triple) or versioning (keep a snapshot of each state). "We believe that for RDF data, labeling is better than versioning."
- Section 1.1: reasons: labeling "preserves the spirit of the distributed and extensible nature of RDF", and "a version management approach accounts only for transaction time, while our approach is apt for handling valid time too."
- Section 1.1: "valid time is the time when data is valid is the modeled" (text as extracted from the PDF, apparently garbled; the sentence defines valid time as the time data holds in the modeled world, and the contrast is with transaction time).
- Section 1.1 and Figure 2: edges are labelled with their interval of validity.
- Section 1.1: "blank nodes introduce many interesting problems", so the temporal graph cannot simply be treated as the union of its snapshots.
