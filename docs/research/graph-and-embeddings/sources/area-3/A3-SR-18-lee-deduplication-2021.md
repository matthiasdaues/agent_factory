# A3-SR-18: Lee et al., Deduplicating Training Data Makes Language Models Better

```json
{
  "source_identity": "Katherine Lee, Daphne Ippolito, Andrew Nystrom, Chiyuan Zhang, Douglas Eck, Chris Callison-Burch, Nicholas Carlini, 'Deduplicating Training Data Makes Language Models Better', arXiv:2107.06499v2; https://arxiv.org/pdf/2107.06499",
  "author_or_issuing_body": "Lee, Ippolito, Nystrom, Zhang, Eck, Carlini (Google Research); Ippolito, Callison-Burch (University of Pennsylvania)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2021-07-01T00:00:00Z",
  "relevant_event_date": "2021-07-01",
  "source_family": "Primary for the two deduplication tools and their parameters. Uses MinHash from Broder (A3-SR-15).",
  "precise_evidence_location": "Abstract; Section 4.1 exact substring matching; Section 4.2 approximate matching with MinHash; Appendix A",
  "method": "Applies exact substring matching with a suffix array and approximate document matching with MinHash on 5-grams, followed by an edit-similarity check, to four language-model training datasets.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v2 of 24 March 2022. The thresholds are set for training-data cleaning, not for claim or idea matching. The author list in the extracted text was partly out of order; it was checked against the title block.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2107.06499 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Exact substring matching identifies verbatim strings that are repeated. This allows us to identify cases where only part of a training example is duplicated"
- Abstract: "Approximate full document matching uses hashbased techniques (Broder, 1997) to identify pairs of documents with high n-gram overlap"
- Section 4.2: "For each pair of documents identified as a potential match, more computationally expensive similarity metrics can be employed as a subsequent filtering step. In particular, we identify two documents as duplicates if they are matched by the MinHash algorithm and their edit similarity is greater than 0.8."
- Appendix A: "For document pairs that were identified as potential matches, we computed their actual Jaccard index, and if that was above 0.8, we computed their edit similarity."
- Shows: a two-stage pattern for near-duplicates: a cheap candidate step (MinHash) and an exact check (Jaccard, then edit similarity). Substring matching covers partial text reuse.
- Does not show: semantic duplicates that share few n-grams.
