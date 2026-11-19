# A2-SR-16: Robertson, Walker, Jones, Hancock-Beaulieu, Gatford, Okapi at TREC-2

```json
{
  "source_identity": "S. E. Robertson, S. Walker, S. Jones, M. M. Hancock-Beaulieu, M. Gatford, 'Okapi at TREC-2', The Second Text REtrieval Conference (TREC-2), NIST Special Publication 500-215, page 21 onward; text at https://trec.nist.gov/pubs/trec2/papers/txt/02.txt",
  "author_or_issuing_body": "City University, London (Okapi team)",
  "publisher": "National Institute of Standards and Technology (NIST)",
  "publication_date": "1994-03-01T00:00:00Z",
  "relevant_event_date": "1993-11-01",
  "source_family": "Primary: the TREC-2 paper that defines BM1, BM11, and BM15. Same team and lineage as A2-SR-14 and A2-SR-15.",
  "precise_evidence_location": "Section 1 Introduction; Section 2.2 The 2-Poisson model and term frequency; Section 2.3 Document length; list of weighting functions after Section 2 (BM1, BM15, BM11); results discussion on pages 24 to 25",
  "method": "System description and experiment report of the City University Okapi system at TREC-2, including results obtained after the official deadline.",
  "limitations": "The NIST text file is an OCR rendering with errors (such as 'TI{EC-2', 'informati6n', and 'if' for tf); quotes keep the OCR text except where noted. The proceedings month is not in the file; March 1994 is my estimate, set to the first day. relevant_event_date is the paper's own statement that it covers work up to November 1993, set to the first of that month.",
  "provenance": "Text file downloaded with curl on 2026-11-18 and converted from Latin-1 to UTF-8 with iconv; found through the TREC-2 proceedings index https://trec.nist.gov/pubs/trec2/t2_proceedings.html. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "This paper reports on City University's work on the TREC-2 project from its commencement up to November 1993." (hyphenation removed.)
- Section 1: "For TREC-1 [1] the "standard" Robertson-Sparck Jones weighting function was used for all runs (equation 1, see also [5])." This is the whole sentence with the source's inner quotation marks; hyphenation and line breaks are removed.
- Section 2.2: "However, there is no obvious reason why any particular function of if should be used in retrieval." (OCR 'if' stands for tf; hyphenation removed.)
- Section 2.2: "It is not by any stretch of the imagination a strong quantitative argument; one may have many reservations about the 2-Poisson model itself, and the transformations sketched above are hardly justifiable in any formal way." and "The constant k1 in the formula is not in any way determined by the argument."
- Section 2.3: "The 2-Poisson model in effect assumes that documents (i.e. records) are all of equal length." It names the "scope hypothesis" and the "verbosity hypothesis", and states: "All the discussion below assumes the verbosity hypothesis; no progress has yet been made with models based on the scope hypothesis."
- Function list: "BM15: 2-Poisson termweights as equation 3 with document length correction as equation 5." and "BM11: 2-Poisson termweights with document length normalisation as equation 4" (OCR shows the 4 as 42; hyphenation removed).
- Results, page 24 to 25: "BM11 appeared slightly less good than BMl5 on the small databases, but later runs on the large databases showed that, with suitable choice of constants, it was substantially, though not uniformly, better."
- Not shown: BM25 itself, which A2-SR-14 introduces at TREC-3.
