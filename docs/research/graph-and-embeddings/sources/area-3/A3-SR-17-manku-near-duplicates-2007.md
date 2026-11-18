# A3-SR-17: Manku, Jain, and Das Sarma, Detecting Near-Duplicates for Web Crawling

```json
{
  "source_identity": "Gurmeet Singh Manku, Arvind Jain, Anish Das Sarma, 'Detecting Near-Duplicates for Web Crawling', WWW 2007; https://research.google.com/pubs/archive/33026.pdf",
  "author_or_issuing_body": "Manku, Jain (Google Inc.); Das Sarma (Stanford University)",
  "publisher": "ACM / IW3C2 (WWW 2007 proceedings); PDF hosted by Google Research",
  "publication_date": "2007-01-01T00:00:00Z",
  "relevant_event_date": "2007-01-01",
  "source_family": "Primary for the application of SimHash to an 8 billion page crawl. Secondary for Charikar's construction (A3-SR-16).",
  "precise_evidence_location": "Abstract; Section 1 contributions; the precision and recall experiment",
  "method": "Computes 64-bit SimHash fingerprints of web pages; searches for fingerprints within a small Hamming distance; tags sampled pairs by hand as true or false positives.",
  "limitations": "Year-only date from the WWW 2007 header; set to 1 January 2007. The manual tagging covers a sample, and the paper reports precision and recall near 0.75 at k = 3. Web pages differ from short claims.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the URL above and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Documents that are exact duplicates of each other (due to mirroring and plagiarism) are easy to identify by standard checksumming techniques. A more difficult problem is the identification of near-duplicate documents."
- Section 1: "simhash is a fingerprinting technique that enjoys the property that fingerprints of near-duplicates differ in a small number of bit positions."
- Section 1: "We experimentally validate that for a repository of 8B webpages, 64-bit simhash fingerprints and k = 3 are reasonable."
- Precision and recall experiment: "Choosing k = 3 is reasonable because both precision and recall are near 0.75."
- Shows: SimHash at web scale with a measured precision and recall near 0.75 on a sample.
- Does not show: detection of paraphrase or same-idea pairs; the method targets pages that differ in small portions.
