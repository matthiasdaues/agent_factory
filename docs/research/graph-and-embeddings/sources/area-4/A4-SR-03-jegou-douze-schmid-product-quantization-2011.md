# A4-SR-03: Jégou, Douze, Schmid, Product Quantization for Nearest Neighbor Search

```json
{
  "source_identity": "Hervé Jégou, Matthijs Douze, Cordelia Schmid, 'Product Quantization for Nearest Neighbor Search', IEEE Transactions on Pattern Analysis and Machine Intelligence 33(1) (2011) 117-128, doi:10.1109/TPAMI.2010.57; HAL postprint inria-00514462v2, read through the mirror https://paper-notes.zhjwpku.com/assets/pdfs/Product_Quantization_for_Nearest_Neighbor_Search.pdf",
  "author_or_issuing_body": "Hervé Jégou, Matthijs Douze, Cordelia Schmid (INRIA)",
  "publisher": "IEEE (journal); postprint deposited in HAL by INRIA",
  "publication_date": "2011-01-01T00:00:00Z",
  "relevant_event_date": "2009-08-01",
  "source_family": "Primary for product quantization and the inverted file with asymmetric distance computation (IVFADC); secondary for E2LSH, FLANN, and the Video-Google inverted file, which it cites.",
  "precise_evidence_location": "Abstract; Section I Introduction; Section IV (non-exhaustive search, coarse quantizer, inverted file, Figure 5)",
  "method": "Algorithm design plus experiments on SIFT and GIST descriptors, up to two billion vectors.",
  "limitations": "The journal issue month is January 2011; the date is set to the first day. relevant_event_date stands for the August 2009 technical report named in the paper. The HAL server refused automated download with a bot check, so the copy came from a third-party mirror; its cover page names HAL inria-00514462v2 and says it is a postprint that corrects reported mistakes, so wording may differ slightly from the journal print.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. The HAL record is https://inria.hal.science/inria-00514462v2; re-verify there or by the DOI."
}
```

## Evidence

- Abstract: "The idea is to decomposes the space into a Cartesian product of low dimensional subspaces and to quantize each subspace separately. A vector is represented by a short code composed of its subspace quantization indices."
- Section I: "However, for real data, LSH is outperformed by heuristic methods, which exploit the distribution of the vectors."
- Section I: "ANN algorithms are typically compared based on the tradeoff between search quality and efficiency. However, this tradeoff does not take into account the memory requirements of the indexing structure. In the case of E2LSH, the memory usage may even be higher than that of the original vectors."
- Section I: "Several multi-dimensional indexing methods, such as the popular KD-tree [5] or other branch and bound techniques, have been proposed to reduce the search time. However, for high dimensions it turns out [6] that such approaches are not more efficient than the brute-force exhaustive distance calculation"
- Section IV: "To avoid exhaustive search we combine an inverted file system [26] with the asymmetric distance computation (IVFADC)."
- Section IV: "The inverted file is the key to the non-exhaustive version of our method."
- Shows: the criticism of LSH (memory, real-data quality) and of trees that led to compressed codes, and the combination of an inverted file with product quantization.
- Does not show: graph-based indexes, which came later, or the cost of retraining the codebooks when the data distribution changes.
