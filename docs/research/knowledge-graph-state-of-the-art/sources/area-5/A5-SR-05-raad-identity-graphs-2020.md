# A5-SR-05: Raad et al., Constructing and Cleaning Identity Graphs in the LOD Cloud

```json
{
  "source_identity": "Joe Raad, Wouter Beek, Frank van Harmelen, Jan Wielemaker, Nathalie Pernelle, Fatiha Sais, 'Constructing and Cleaning Identity Graphs in the LOD Cloud', Data Intelligence 2(2020) 323-352, doi:10.1162/dint_a_00057; https://ir.cwi.nl/pub/30875/30875.pdf",
  "author_or_issuing_body": "Raad, Beek, van Harmelen, Wielemaker (Vrije Universiteit Amsterdam); Pernelle, Sais (Universite Paris Sud)",
  "publisher": "MIT Press / Chinese Academy of Sciences (Data Intelligence); PDF hosted by CWI",
  "publication_date": "2020-01-01T00:00:00Z",
  "relevant_event_date": "2018-01-01",
  "source_family": "Primary for its own method; secondary for the earlier sameAs.cc dataset (Beek et al., ESWC 2018) and the 2018 error-degree method (Raad et al., ISWC 2018), which it summarises and cites. Cites Halpin et al. (A5-SR-04) as reference [3].",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 3.2 Error Degree Computation; error degree distribution (Figure 3)",
  "method": "Describes an identity graph built from the LOD-a-lot collection, community detection on each identity cluster, error degrees per owl:sameAs link, and subgraphs cut at chosen error degrees.",
  "limitations": "Year-only date; set to 1 January 2020 (the PDF states received August 2019). relevant_event_date 2018-01-01 stands for the 2018 prior work and is approximate. The error degree is a network-based estimate; it is not a proven measure of correctness. The paper reports distribution of error degrees, not a labelled precision figure for the whole graph. The two 2018 papers were not read in full text.",
  "provenance": "PDF downloaded with curl on 2026-11-17 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Studies that date back as far as 2009, observed that the owl:sameAs property is sometimes used incorrectly. In our previous work, we presented an identity graph containing over 500 million explicit and 35 billion implied owl:sameAs statements, and presented a scalable approach for automatically calculating an error degree for each identity statement."
- Abstract: "even though the Semantic Web contains many erroneous owl:sameAs statements, it is still possible to use Semantic Web data while at the same time minimising the adverse effects of misusing owl:sameAs."
- Section 1: "An RDF statement of the form 'x owl:sameAs y' indicates that every property attributed to x must also be attributed to y, and vice versa." No central naming authority enforces a unique name assumption.
- Section 3.2: an error degree is assigned to each link from the community structure of its identity cluster (intra-community and inter-community links).
- Results: around 73% of statements have an error degree below 0.4; around 5% have an error degree above 0.8 (Figure 3 discussion).
- Not shown: any change to the OWL semantics. The approach keeps sameAs and filters links.
