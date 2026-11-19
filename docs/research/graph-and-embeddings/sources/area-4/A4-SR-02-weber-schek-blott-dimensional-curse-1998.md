# A4-SR-02: Weber, Schek, Blott, A Quantitative Analysis and Performance Study for Similarity-Search Methods in High-Dimensional Spaces

```json
{
  "source_identity": "Roger Weber, Hans-J. Schek, Stephen Blott, 'A Quantitative Analysis and Performance Study for Similarity-Search Methods in High-Dimensional Spaces', Proceedings of the 24th VLDB Conference, New York, 1998, pp. 194-205; https://www.vldb.org/conf/1998/p194.pdf",
  "author_or_issuing_body": "Roger Weber, Hans-J. Schek (ETH Zurich); Stephen Blott (Bell Laboratories)",
  "publisher": "VLDB Endowment (conference proceedings hosted at vldb.org)",
  "publication_date": "1998-08-01T00:00:00Z",
  "relevant_event_date": "1998-08-01",
  "source_family": "Primary for the analysis of tree-based and partitioning indexes in high dimensions and for the VA-file.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (contributions); experimental section comparing R*-tree, X-tree, and VA-file",
  "method": "Analytical cost model of partitioning and clustering indexes plus experiments on synthetic and image-feature data.",
  "limitations": "Only the year and the conference month are known; the date is set to 1 August 1998. The PDF is a scan with OCR, so some words carry OCR errors; quotes avoid the damaged passages. The analysis covers exact search with partitioning indexes, not approximate methods.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We show formally that these methods exhibit linear complexity at high dimensionality, and that existing methods are outperformed on average by a simple sequential scan if the number of dimensions exceeds around 10."
- Section 1: "We demonstrate that these methods are outperformed by a sequential scan whenever the dimensionality is above 10."
- Shows: the criticism of tree-based and partitioning indexes for exact search above roughly ten dimensions, and the VA-file response, which speeds up the sequential scan instead of avoiding it.
- Does not show: anything about approximate search, LSH, quantization, or graph indexes.
