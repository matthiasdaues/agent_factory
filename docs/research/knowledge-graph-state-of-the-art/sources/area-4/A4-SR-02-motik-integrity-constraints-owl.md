# A4-SR-02: Motik, Horrocks, Sattler: integrity constraints for OWL (extended version)

```json
{
  "source_identity": "Boris Motik, Ian Horrocks, Ulrike Sattler. 'Bridging the Gap Between OWL and Relational Databases'. Extended version of 'Adding Integrity Constraints to OWL' (OWLED 2007) and of the WWW 2007 paper of the same title. Journal of Web Semantics 7(2), 2009, pp. 74-89. Copy read: https://www.cs.ox.ac.uk/people/ian.horrocks/Publications/download/2009/MoHS09a.pdf",
  "author_or_issuing_body": "Boris Motik and Ian Horrocks (Computing Laboratory, University of Oxford); Ulrike Sattler (University of Manchester)",
  "publisher": "Author copy hosted by the University of Oxford; journal publisher Elsevier",
  "publication_date": "2007-09-13T00:00:00Z",
  "relevant_event_date": "2007-09-13",
  "source_family": "Primary. Peer-reviewed line of work by Motik, Horrocks, and Sattler (WWW 2007, OWLED 2007, J. Web Semantics 2009). The Oxford copy read here is the manuscript dated 13 September 2007, so the journal version may differ.",
  "precise_evidence_location": "Abstract (page 1); Section 1 'Introduction' (pages 2-3), the tax-return example and the list of contributions; Section 3 on extended knowledge bases with an integrity-constraint TBox and minimal models",
  "method": "Downloaded the PDF on 2026-11-17, extracted its text with pdftotext, and read the abstract, introduction, and the opening of Section 3.",
  "limitations": "The date 2007-09-13 is the manuscript date on the title page. The journal appeared in 2009, and the exact day is not recorded here. Only the abstract, introduction, and the start of the minimal-model definitions were read. The algorithms and the proofs were not checked. The paper proposes a semantics. It reports no adoption by OWL tools.",
  "provenance": "Downloaded from the Oxford URL above on 2026-11-17 with curl. Re-verify by opening the PDF and reading the abstract on page 1. The journal DOI given by a search result is 10.1016/j.websem.2009.02.001; that DOI page was not fetched."
}
```

## Evidence

### Criticism of OWL as a checking language

- Abstract: "The schema statements in relational databases are usually interpreted as integrity constraints (ICs) and are used to check whether the data is structured according to the schema. OWL allows for axioms that resemble integrity constraints; however, these axioms are interpreted under the standard first-order semantics and not as checks."
- Section 1: "adding a person without a social security number to an OWL knowledge base does not raise an error, but only leads to the inference that the person in question has some (unknown) social security number."
- Section 1: "In fact, in OWL it is not possible to formalize integrity constraints that behave as checks, which has caused problems in practice."

### The proposed formulation

- Section 1, contributions: the schema "is separated into the standard TBox that contains axioms which are interpreted as usual, and the integrity constraint TBox that contains axioms which are interpreted as checks." Satisfaction of the constraints is defined "based on the notion of minimal models."
- Section 1 also notes the earlier epistemic approaches and says they "do not affect TBox reasoning at all, and they are only applied to ABox individuals."

### What this record supports

- It records the first formulation in the concept history "Constraint semantics for OWL axioms": OWL syntax with a minimal-model reading for checks (area index, concept 1, step 2).
