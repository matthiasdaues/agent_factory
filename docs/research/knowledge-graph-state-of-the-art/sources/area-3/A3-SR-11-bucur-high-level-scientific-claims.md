# A3-SR-11 — Bucur et al., "Expressing High-Level Scientific Claims with Formal Semantics" (2021)

```json
{
  "source_identity": "Bucur, C.-I., Kuhn, T., Ceolin, D., van Ossenbruggen, J., 'Expressing High-Level Scientific Claims with Formal Semantics', K-CAP '21, 2-3 December 2021, arXiv:2109.12907v3",
  "author_or_issuing_body": "Cristina-Iulia Bucur, Tobias Kuhn, Jacco van Ossenbruggen (Vrije Universiteit Amsterdam), Davide Ceolin (CWI)",
  "publisher": "ACM (K-CAP 2021 proceedings); arXiv preprint read",
  "publication_date": "2021-10-29T00:00:00Z",
  "relevant_event_date": "2021-09-01",
  "source_family": "Primary. Research paper from the same group as A3-SR-07 to A3-SR-09; it builds on the nanopublication lineage and tests what RDF and OWL can express about claims.",
  "precise_evidence_location": "Abstract; Section 2 (background paragraph on nanopublications, three basic elements).",
  "method": "The authors analyze the main claims of a sample of scientific articles from all disciplines, derive a pattern, and test with knowledge representation experts how consistently they apply it.",
  "limitations": "Publication date is that of arXiv version 3; the event date is the month of the arXiv identifier (September 2021), first day used. Only the abstract and the nanopublication background paragraph were read in detail. Sample sizes and agreement figures were not extracted. The paper does not criticize the nanopublication specification itself; the criticism is aimed at plain RDF and OWL as a way to express claims. It does not show that the 'super-pattern' was adopted by any specification.",
  "provenance": "Fetched 2026-11-17 via the WebFetch tool's saved copy of https://arxiv.org/pdf/2109.12907 and converted with pdftotext. Quotes are exact and were checked against the extracted text."
}
```

## Evidence

- Abstract: "The core claims or hypotheses of scientific work have only been covered in a shallow manner, such as by linking mentioned entities to established identifiers."
- Abstract: "Analyzing the main claims from a sample of scientific articles from all disciplines, we find that their semantics are more complex than what a straight-forward application of formalisms like RDF or OWL account for, but we managed to elicit a clear semantic pattern which we call the 'super-pattern'."
- Abstract: "the instantiation of the five slots of this super-pattern leads to a strictly defined statement in higher-order logic."
- Abstract: experts "show a high degree of consistency and convergence given the complexity of the task and the subject."
- Section 2: nanopublications "contain just three basic elements (represented in RDF): an assertion containing a small unit of information that is its main content (such as a scientific finding), provenance of the assertion [...] and a publication information part about the nanopublication as a whole".

## What the source shows

It shows a 2021 finding that claims in published articles need more than a direct RDF or OWL encoding, and a five-slot pattern that maps to higher-order logic. It also shows that the three-part nanopublication structure was still the reference in 2021.

## What the source does not show

It does not show an effect on the nanopublication format. It does not show how well the pattern works outside the tested sample.

## Failed searches and gaps

The sample size and the agreement scores are unread.
