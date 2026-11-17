# A5-SR-14: Idrissou et al., Network Metrics for Assessing the Quality of Entity Resolution

```json
{
  "source_identity": "Al Idrissou, Frank van Harmelen, Peter van den Besselaar, 'Network Metrics for Assessing the Quality of Entity Resolution Between Multiple Datasets', preprint, https://www.few.vu.nl/~frankh/postscript/EKAW2018.pdf",
  "author_or_issuing_body": "Al Idrissou, Frank van Harmelen (Vrije Universiteit Amsterdam, computer science); Peter van den Besselaar (Vrije Universiteit Amsterdam, organization sciences)",
  "publisher": "Author-hosted preprint at Vrije Universiteit Amsterdam",
  "publication_date": "2018-07-13T00:00:00Z",
  "relevant_event_date": "2018-07-13",
  "source_family": "Primary. Shares authors and the community-detection idea with the identity-graph work of A5-SR-05 (van Harmelen is an author of both).",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 Identity Link Networks",
  "method": "Proposes a network metric over links between entities of several datasets, and tests it against a gold standard built for six datasets and against one published gold standard.",
  "limitations": "The date is the PDF creation date (13 July 2018), not a publication date. The file name suggests the EKAW 2018 conference; the text read does not state a venue, so the venue is not recorded. Domain is science, technology and innovation studies, not general knowledge graphs. Results are the authors' own.",
  "provenance": "PDF downloaded with curl on 2026-11-17 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "much less work has been done on how to assess the quality of such entity links once they have been generated." Evaluation is limited to ground truth, manual work or crowd sourcing.
- Abstract: "links between entities from multiple datasets form a network, and we show how simple metrics on this network can reliably predict their quality."
- Section 1: the problem "is greatly exacerbated for entity resolution between more than two datasets, because the number of possible links grows rapidly with the number of datasets."
- Section 2: an Identity Link Network is "a network of links between entities from a number of datasets that are found by one or more entity resolution algorithms to represent the same real world entity."
- Not shown: results on owl:sameAs links of the LOD Cloud; that is A5-SR-05.
