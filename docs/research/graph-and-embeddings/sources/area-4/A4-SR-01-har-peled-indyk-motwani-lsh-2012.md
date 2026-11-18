# A4-SR-01: Har-Peled, Indyk, Motwani, Approximate Nearest Neighbor: Towards Removing the Curse of Dimensionality

```json
{
  "source_identity": "Sariel Har-Peled, Piotr Indyk, Rajeev Motwani, 'Approximate Nearest Neighbor: Towards Removing the Curse of Dimensionality', Theory of Computing 8 (2012) 321-350; https://theoryofcomputing.org/articles/v008a014/v008a014.pdf",
  "author_or_issuing_body": "Sariel Har-Peled, Piotr Indyk, Rajeev Motwani",
  "publisher": "Theory of Computing (open-access journal), special issue in honor of Rajeev Motwani",
  "publication_date": "2012-07-16T00:00:00Z",
  "relevant_event_date": "1998-05-01",
  "source_family": "Primary for the locality-sensitive hashing (LSH) method as its authors restate it; this is the journal version that unifies the STOC 1998 paper of Indyk and Motwani and a FOCS 2001 paper. The STOC 1998 paper itself was not read.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (curse of dimensionality, two techniques); Section 3, Definition 3.3 (locality-sensitive family)",
  "method": "Theoretical algorithms with proofs of space and query-time bounds for the c-approximate nearest neighbor problem; no experiments.",
  "limitations": "relevant_event_date stands for STOC 1998 and is set to the first day of May 1998; the exact conference day was not checked. The journal text is a later rewrite, so its wording is not the 1998 wording. Only the abstract, the introduction, and Section 3 were read. The paper gives worst-case bounds, not measured search quality on real data.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We present two algorithms for the approximate nearest neighbor problem in high-dimensional spaces. For data sets of size n living in Rd , the algorithms require space that is only polynomial in n and d, while achieving query times that are sub-linear in n and polynomial in d."
- Abstract: "The article is based on the material from the authors’ STOC’98 and FOCS’01 papers. It unifies, generalizes and simplifies the results from those papers."
- Section 1: "The lack of success in removing the exponential dependence on the dimension led many researchers to conjecture that no efficient solutions exists for these problems when the dimension is large enough"
- Section 1: "Its key idea is to hash the points in a way that the probability of collision is much higher for objects which are close to each other than for those which are far apart."
- Shows: the formulation of LSH as a hash family with a higher collision probability for close points, and the motivation from the exponential cost of exact methods in high dimensions.
- Does not show: measured recall or speed on real datasets, memory use in practice, or behaviour under inserts and deletes.
