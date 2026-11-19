# A3-SR-10: Weller, Lawrie, and Van Durme, NevIR: Negation in Neural Information Retrieval

```json
{
  "source_identity": "Orion Weller, Dawn Lawrie, Benjamin Van Durme, 'NevIR: Negation in Neural Information Retrieval', arXiv:2305.07614v2; https://arxiv.org/pdf/2305.07614",
  "author_or_issuing_body": "Weller, Lawrie, Van Durme (Johns Hopkins University)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2023-05-01T00:00:00Z",
  "relevant_event_date": "2023-05-01",
  "source_family": "Primary for the NevIR benchmark and its results.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; the section that lists the evaluated models (bi-encoders, cross-encoders, random baseline)",
  "method": "Builds pairs of documents that differ only by negation, with one query for each; a model scores a point only when it ranks the right document first for both queries. Compares sparse, bi-encoder, late-interaction, and cross-encoder models.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v2 of 26 February 2024; the venue was not checked in the PDF. The documents are short and built by crowd workers. The benchmark tests ranking of two documents, not a similarity threshold.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2305.07614 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We therefore construct a straightforward benchmark on this theme: asking IR models to rank two documents that differ only by negation."
- Abstract: "the results vary widely according to the type of IR architecture: cross-encoders perform best, followed by late-interaction models, and in last place are bi-encoder and sparse neural architectures."
- Abstract: "We find that most information retrieval models (including SOTA ones) do not consider negation, performing the same or worse than a random ranking."
- Section 1: "bi-encoder representations of the two documents are nearly identical despite negation words and that late-interaction models such as ColBERT ignore negation words in the MaxSim operator."
- Model list, random baseline: "the expected mean pairwise accuracy is 25%"
- Shows: negation as a limit of embedding similarity, and the cross-encoder as the strongest of the tested checks.
- Does not show: that any tested model reaches human performance; the abstract states a large gap remains.
