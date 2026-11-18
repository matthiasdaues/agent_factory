# A3-SR-16: Charikar, Similarity Estimation Techniques from Rounding Algorithms (SimHash)

```json
{
  "source_identity": "Moses S. Charikar, 'Similarity Estimation Techniques from Rounding Algorithms', STOC 2002; copy at https://www.cs.princeton.edu/courses/archive/spr04/cos598B/bib/CharikarEstim.pdf",
  "author_or_issuing_body": "Moses S. Charikar (Princeton University)",
  "publisher": "ACM (Proceedings of STOC 2002); copy hosted on a Princeton University course page",
  "publication_date": "2002-05-19T00:00:00Z",
  "relevant_event_date": "2002-05-19",
  "source_family": "Primary for the random-hyperplane hash that later work calls SimHash. Builds on min-wise permutations (A3-SR-15). Used by A3-SR-17.",
  "precise_evidence_location": "Abstract; Section 1 Introduction",
  "method": "Theoretical construction of locality-sensitive hash schemes from rounding algorithms, including a scheme for the angle between vectors.",
  "limitations": "The paper is theory; it does not evaluate near-duplicate detection on documents. The name SimHash is not used in the paper; A3-SR-17 uses it. The hash as an index family belongs to area 4.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the URL above and extracted with pdftotext. Re-verify at the URL above or in the ACM Digital Library."
}
```

## Evidence

- Abstract: "Min-wise independent permutations provide an elegant construction of such a locality sensitive hashing scheme for a collection of subsets with the set similarity measure"
- Abstract: "This yields a sketching scheme for estimating the cosine similarity measure between two vectors, as well as a simple alternative to minwise independent permutations for estimating set similarity."
- Section 1: "the advantage of a locality sensitive hashing based scheme is that this directly yields techniques for nearest neighbor search for the cosine similarity measure."
- Shows: the step from set similarity (MinHash) to a bit sketch for cosine similarity between weighted vectors.
- Does not show: any empirical check of near-duplicate quality.
