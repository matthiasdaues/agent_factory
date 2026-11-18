# A2-SR-11: Cormack, Clarke, Büttcher, Reciprocal Rank Fusion, SIGIR 2009

```json
{
  "source_identity": "G. V. Cormack, C. L. A. Clarke, Stefan Büttcher, 'Reciprocal Rank Fusion outperforms Condorcet and individual Rank Learning Methods', SIGIR '09, July 19-23, 2009, Boston; doi:10.1145/1571941.1572114; PDF https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf",
  "author_or_issuing_body": "G. V. Cormack, C. L. A. Clarke (University of Waterloo); Stefan Büttcher (Google)",
  "publisher": "ACM (SIGIR 2009 proceedings); PDF hosted by the University of Waterloo",
  "publication_date": "2009-07-19T00:00:00Z",
  "relevant_event_date": "2009-07-19",
  "source_family": "Primary: the original paper that defines RRF. Cites Montague and Aslam (Condorcet Fuse, CIKM 2002) and compares with CombMNZ from Fox and Shaw (A2-SR-12).",
  "precise_evidence_location": "Section 1 Reciprocal Rank Fusion (formula and choice of k); Table 1 (effect of k on MAP); Section 2 Discussion",
  "method": "Two-page poster paper. Fuses runs of the Wumpus search system and submitted TREC runs, and the LETOR 3 baselines; compares mean average precision with Condorcet Fuse and CombMNZ.",
  "limitations": "Short poster paper with MAP as the main measure. The experiments fuse many runs of lexical systems and learning-to-rank methods; none fuses a lexical ranking with a dense vector ranking. The publication_date is the first day of the conference. The DOI is from my knowledge of the ACM listing and was not checked against the ACM site.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext, with and without -layout. In the two-column layout the sentence that starts Our intuition runs across a column break and the copyright footnote; the quote joins its two parts. Re-verify at the PDF URL above."
}
```

## Evidence

- Section 1: "In the search for such a method we came up with Reciprocal Rank Fusion (RRF) to serve as a baseline."
- Section 1, the formula: the score of a document d is the sum over rankings r of 1 / (k + r(d)), "where k = 60 was fixed during a pilot investigation and not altered during subsequent validation." (The formula is typeset; I give it in words.)
- Section 1: "Our intuition in choosing this formula derived from fact that while highly-ranked documents are more important, the importance of lower-ranked documents does not vanish as it would were, say, an exponential function used. The constant k mitigates the impact of high rankings by outlier systems."
- Section 1, pilot: "The results of the first, shown in table 1, indicated that k = 60 was near-optimal, but that the choice was not critical." Table 1 shows MAP from .2072 at k = 0 to .2147 at k = 80.
- Section 2: "RRF is simpler and more effective than Condorcet Fuse, while sharing the valuable property that it combines ranks without regard to the arbitrary scores returned by particular ranking methods".
- Section 2: "RRF requires no special voting algorithm or global information; ranks may be computed and summed one system at a time, avoiding the necessity of keeping all rankings in memory."
- Section 2, on the score-based method: "CombMNZ multiplies the sum of the uncalibrated scores of individual system by the sum of a binary quantization of each rank." The authors find its results have higher variance.
- Not shown: weights per ranking, and any fusion of lexical and dense vector retrieval.
