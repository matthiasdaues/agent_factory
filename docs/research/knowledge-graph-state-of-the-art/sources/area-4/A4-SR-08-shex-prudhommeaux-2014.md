# A4-SR-08: Prud'hommeaux, Labra Gayo, Solbrig: Shape Expressions

```json
{
  "source_identity": "Eric Prud'hommeaux, Jose Emilio Labra Gayo, Harold Solbrig. 'Shape Expressions: An RDF validation and transformation language'. SEMANTiCS 2014 (SEM '14), Leipzig, pp. 32-40, DOI 10.1145/2660517.2660523. Copy read: http://labra.weso.es/pdf/2014_ShEx.pdf",
  "author_or_issuing_body": "Eric Prud'hommeaux (W3C/MIT), Jose Emilio Labra Gayo (University of Oviedo), Harold Solbrig (Mayo Clinic)",
  "publisher": "ACM, 10th International Conference on Semantic Systems; author copy hosted by Labra Gayo",
  "publication_date": "2014-09-04T00:00:00Z",
  "relevant_event_date": "2014-09-04",
  "source_family": "Primary. Peer-reviewed conference paper that introduces Shape Expressions. Its authors also took part in the RDF Validation Workshop (record 6).",
  "precise_evidence_location": "Abstract; Section 1 'Introduction'; Section 4 (paragraph beginning 'Special care has to be taken for recursive definitions'); Section 7 'Related Work', first two bullets",
  "method": "Downloaded the PDF on 2026-11-17, extracted its text with pdftotext, and read the abstract, introduction, the recursion paragraph, and the related-work section.",
  "limitations": "The date is the first day of the conference given in the paper's copyright block (4-5 September 2014). The semantics section was read only for the recursion paragraph. The paper defines ShEx in 2014. It does not cover ShEx 2.0 or 2.1, which changed the language. The related-work section is the authors' own view of competing approaches.",
  "provenance": "Downloaded from the Labra Gayo URL above on 2026-11-17 with curl. Re-verify by reading page 1 and the Related Work section."
}
```

## Evidence

### Criticism of OWL and SPARQL for validation

- Introduction: "although there are standards for inference like RDF Schema and OWL, these technologies employ Open World and Non-Unique Name Assumptions that creates difficulties for validation purposes."
- Section 7, first bullet: "what triggers constraint violations in closed world systems leads to new inferences in standard OWL systems. [7, 22, 14] propose the use of OWL expressions with a Closed World Assumption to express integrity constraints." Those references are the OWLED 2009 and AAAI 2010 papers and the Motik et al. paper (records 2 to 4).
- Section 7, second bullet: "SPARQL-based approaches use the SPARQL Query Language to express the validation constraints." The bullet goes on to weigh SPARQL's expressiveness. That part was not read closely.

### The formulation

- Abstract: "a Shape Expression definition language which enables RDF validation through the declaration of constraints on the RDF model," with syntax and "formal semantics using inference rules," and a language built on "regular expressions."
- Introduction: ShEx "is intended to perform the same function for RDF graphs as Schema languages to XML."

### Recursion

- Section 2: "Notice that it is also possible to have recursive references."
- Section 4: "Special care has to be taken for recursive definitions. To avoid infinite loops, we add the current type to the context in the definition of matchShape."

### What this record supports

- It records the first ShEx formulation, with recursion allowed and handled by a typing context (area index, concept 2, step 4; concept 3, step 2).
