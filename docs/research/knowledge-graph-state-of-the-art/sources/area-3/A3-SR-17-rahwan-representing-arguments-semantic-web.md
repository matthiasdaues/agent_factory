# A3-SR-17 — Rahwan et al., "Representing and classifying arguments on the Semantic Web" (2011)

```json
{
  "source_identity": "Rahwan, I., Banihashemi, B., Reed, C., Walton, D., Abdallah, S., 'Representing and classifying arguments on the Semantic Web', The Knowledge Engineering Review 26(4), 487-511, DOI 10.1017/S0269888911000191",
  "author_or_issuing_body": "Iyad Rahwan, Bita Banihashemi, Chris Reed, Douglas Walton, Sherief Abdallah",
  "publisher": "Cambridge University Press (journal); the copy read is a preview PDF at maxapress.com",
  "publication_date": "2011-01-01T00:00:00Z",
  "relevant_event_date": "2011-01-01",
  "source_family": "Primary. Follow-up to A3-SR-15 by two of its authors (Rahwan, Reed). It states the limits of the ontology in A3-SR-15.",
  "precise_evidence_location": "Abstract; Section 2.2 (limitations of Web 2.0 argumentation tools); end of Section 2.3 (sentence on ArgDF limitations); Section 3.4 (redundancy in the ArgDF reification); Section 4.",
  "method": "A design paper: a Description Logic ontology for arguments, OWL reasoning over argument structures, and a pilot Web system.",
  "limitations": "Only the year 2011 was verified (volume 26, issue 4); the first day of the year is used for both dates. The preview PDF may be incomplete; 25 pages were extracted. The paper states that ArgDF 'suffers from number of limitations (discussed below)' but, in the text read, spells out only the redundancy at instance level. The paper evaluates a pilot system, not a deployed one.",
  "provenance": "Fetched 2026-11-17 with curl from https://maxapress.com/data/article/ker/preview/pdf/S0269888911000191.pdf and converted with pdftotext. Quotes are exact and were checked against the extracted text."
}
```

## Evidence

- Abstract: "we present a Description Logic ontology for annotating arguments, based on a new reification of the AIF and founded in Walton's theory of argumentation schemes." Web Ontology Language reasoning "enables significantly enhanced querying of arguments through automatic scheme classifications, instance classification, inference of indirect support in chained argument structures, and inference of critical questions."
- End of Section 2.3: "However, the underlying ontology of ArgDF suffers from number of limitations (discussed below), both in terms of design specification and the ontology language used."
- Section 3.4: "From the above, it is clear that ArgDF's reification of the AIF causes some redundancy at the instance level. Both arguments and schemes are described with explicit structure at the instance level. As a result, the property 'fulfilsScheme' does not capture the fact that an S-node represents an instantiation of some generic class of arguments (i.e. scheme)."
- Section 3.4: "The AIF model is reified by interpreting schemes as classes and S-nodes as instances of those classes; in this case, the semantics of the 'uses' edge can be interpreted as 'instance-of'."
- Section 2.2: in Web 2.0 argumentation tools such as Truthmapping, "arguments are structured and possibly hyper-linked, these links carry no explicit semantics."

## What the source shows

It shows a fourth AIF formulation (2011): schemes become classes and S-nodes become their instances, written in OWL. It states the reason: redundancy in the 2007 RDFS reification and the loss of reasoning over scheme classes.

## What the source does not show

It does not show the other ArgDF limitations the authors promise to discuss, and it does not show adoption of the OWL ontology. It does not mention nanopublications or PROV.

## Failed searches and gaps

A later account of the Argument Web (Springer, Philosophy & Technology 2017, found by search) was not read.
