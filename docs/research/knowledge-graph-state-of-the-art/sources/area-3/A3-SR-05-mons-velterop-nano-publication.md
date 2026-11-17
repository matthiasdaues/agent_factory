# A3-SR-05 — Mons and Velterop, "Nano-Publication in the e-science era" (2009)

```json
{
  "source_identity": "Mons, B. and Velterop, J., 'Nano-Publication in the e-science era', Workshop on Semantic Web Applications in Scientific Discourse (SWASD 2009), CEUR-WS Vol-523, http://ceur-ws.org/Vol-523/Mons.pdf",
  "author_or_issuing_body": "Barend Mons and Jan Velterop, Concept Web Alliance and Netherlands BioInformatics Centre",
  "publisher": "CEUR Workshop Proceedings (CEUR-WS.org)",
  "publication_date": "2009-10-26T00:00:00Z",
  "relevant_event_date": "2009-10-26",
  "source_family": "Primary. Origin paper of the nanopublication idea, from the Concept Web Alliance. Later nanopublication papers (A3-SR-06 onward) cite this lineage and are not independent of it.",
  "precise_evidence_location": "Abstract; Section 1 (second paragraph); Section 2.3 'The Third Step: Annotation of Statements with Context and Provenance', paragraphs 1 and 3.",
  "method": "A position paper. Section 1 calls it 'a plea, not a research paper'. It argues by reasoning and gives no experiment.",
  "limitations": "The workshop date (26 October 2009) stands in for the proceedings date, which was not verified. The paper defines no data structure, no RDF serialization and no named-graph layout. It uses the word 'nano-publication' but the extracted text gives no formal definition. The authors write for a life-science audience and from inside the Concept Web Alliance, which promoted the idea.",
  "provenance": "Fetched 2026-11-17 with curl from http://ceur-ws.org/Vol-523/Mons.pdf and converted with pdftotext. Quotes are exact and were checked against the extracted text. Re-verify with the same URL."
}
```

## Evidence

- Abstract: the paper "attempts a stepwise explanation of the use of richly annotated RDF statements as carriers of unambiguous, meta-analyzed information in the form of traceable nano-publications."
- Section 1: "a paper like this is a plea, not a research paper, and therefore relies on verbal reasoning more than a presentation of research results usually does".
- Section 2.3: "If a dogmatic triple approach were chosen, each connection would again be a triple and the triple store representing biomedical knowledge in RDF would explode."
- Section 2.3: "'richly annotated triples', a term in fact standing for disambiguated, non-redundant statements in proper context and with proper provenance."
- Section 2.3: "Statements should be treated as the smallest building blocks of ontologies".
- Section 2.3: "Provenance is included here in the context of a statement." Typical provenance listed: the person who made the statement, its source, a time stamp, ownership and "most importantly: status".

## What the source shows

It shows the first documented form of the idea in this lineage: a statement carries its context and provenance, and the statement is the unit of publication.

## What the source does not show

It does not show a technical model, a serialization, or any criticism of an earlier formulation. The stated reason for the design is that one triple per connection would make the store "explode".

## Failed searches and gaps

No earlier Concept Web Alliance text (the 2009 declaration cited by A3-SR-06) was fetched.
