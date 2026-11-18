# A3-SR-15: Broder, On the Resemblance and Containment of Documents

```json
{
  "source_identity": "Andrei Z. Broder, 'On the resemblance and containment of documents', Compression and Complexity of Sequences 1997; copy at https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf",
  "author_or_issuing_body": "Andrei Z. Broder (Digital Systems Research Center, Palo Alto)",
  "publisher": "IEEE (proceedings of SEQUENCES 1997); copy hosted on a Princeton University course page",
  "publication_date": "1997-01-01T00:00:00Z",
  "relevant_event_date": "1997-01-01",
  "source_family": "Primary for resemblance, containment, and shingling with min-wise sampling (MinHash). Cited by A3-SR-16, A3-SR-18.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; the definitions of shingling, resemblance, and containment that follow it",
  "method": "Defines resemblance and containment as set-intersection measures over word shingles and estimates them from small random sketches; clusters 30 million web documents.",
  "limitations": "Year-only date; set to 1 January 1997. The copy carries no venue stamp; the venue is taken from the title and standard citation. The copy is a course mirror, not the publisher version.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the URL above and extracted with pdftotext. Re-verify at the URL above or in IEEE Xplore."
}
```

## Evidence

- Abstract: "Given two documents A and B we define two mathematical notions: their resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of “roughly the same” and “roughly contained.”"
- Section 1: "These informal concepts do not seem to be well captured by any of the standard distances defined on strings (Hamming, Levenshtein, etc.)."
- Section 1: "Our approach to determining syntactic similarity is related to the sampling approach developed independently by Heintze [6]"
- Section 1: "We calculated our clusters based on a 50% resemblance."
- Shows: near-duplicate and text reuse detection as syntactic overlap, with containment as a directed measure (A in B).
- Does not show: any treatment of meaning; the measure is syntactic by the author's own words.
