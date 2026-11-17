# A4-SR-03: Sirin and Tao: Towards Integrity Constraints in OWL

```json
{
  "source_identity": "Evren Sirin, Jiao Tao. 'Towards Integrity Constraints in OWL'. OWLED 2009, CEUR-WS Vol-529, pp. 79-88. https://ceur-ws.org/Vol-529/owled2009_submission_35.pdf",
  "author_or_issuing_body": "Evren Sirin (Clark & Parsia, Washington DC) and Jiao Tao (Rensselaer Polytechnic Institute)",
  "publisher": "CEUR Workshop Proceedings (CEUR-WS.org), OWL: Experiences and Directions 2009",
  "publication_date": "2009-10-23T00:00:00Z",
  "relevant_event_date": "2009-10-23",
  "source_family": "Primary. Workshop paper by the authors who later built the Pellet integrity constraint validator. Shares authors with the AAAI 2010 paper (record 4), so the two are not independent of each other.",
  "precise_evidence_location": "Abstract and Section 1 'Introduction' (page 1-2, the product and manufacturer example); Section 3 discussion of existing proposals; Section 5 prototype with Pellet",
  "method": "Downloaded the PDF on 2026-11-17, extracted its text with pdftotext, and read the abstract and the first two pages. Section 3 and 5 content is taken from the paper's own overview paragraph.",
  "limitations": "The workshop date 2009-10-23 is the first day of OWLED 2009 as reported by a search result, not a date printed on the paper. The criticism of Motik et al. is stated here only as 'not completely satisfied'. The detailed counterexamples are in record 4. The paper reports preliminary results only. Sections 3 to 5 were not read in full.",
  "provenance": "Downloaded from the CEUR URL above on 2026-11-17 with curl. Re-verify by reading the abstract on page 1."
}
```

## Evidence

### Why OWL's semantics blocks validation

- Abstract: "specific aspects of OWL's standard semantics, i.e., the Open World Assumption (OWA) and the absence of Unique Name Assumption (UNA), make it difficult to use OWL in this way. What triggers a constraint violation in closed world systems leads to new inferences in standard OWL systems."
- Section 1: "It is possible in OWL to express the requirement that every product has a manufacturer but due to OWA not having the manufacturer information for a product in the KB would not cause a logical inconsistency and cannot be used directly for detection."

### Position toward the earlier proposal

- Section 1: "Our work is in line with recent research by Motik et al. [9] where ICs are written as standard OWL axioms but are interpreted with a different semantics for data validation purposes."
- Section 1 lists "why we are not completely satisfied with existing solution" as the subject of Section 3.

### The proposed formulation

- Abstract: the paper defines "an Integrity Constraint (IC) semantics for OWL axioms," shows that "IC validation problem can be reduced to SPARQL query answering using off-the-shelf reasoner," and presents "a prototype implementation using Pellet."
- Section 2 reports a user survey on constraint requirements, published on the Web and advertised on mailing lists.

### What this record supports

- It records the second formulation in concept 1: closed-world checking with a weak unique name assumption, reducible to SPARQL queries (area index, concept 1, step 3).
