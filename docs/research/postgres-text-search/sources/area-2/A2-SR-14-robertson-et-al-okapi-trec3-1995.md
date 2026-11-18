# A2-SR-14: Robertson, Walker, Jones, Hancock-Beaulieu, Gatford, Okapi at TREC-3

```json
{
  "source_identity": "S. E. Robertson, S. Walker, S. Jones, M. M. Hancock-Beaulieu, M. Gatford, 'Okapi at TREC-3', Overview of the Third Text REtrieval Conference (TREC-3), NIST Special Publication 500-225; PostScript at https://trec.nist.gov/pubs/trec3/papers/city.ps.gz",
  "author_or_issuing_body": "Centre for Interactive Systems Research, Department of Information Science, City University, London",
  "publisher": "National Institute of Standards and Technology (NIST)",
  "publication_date": "1995-01-01T00:00:00Z",
  "relevant_event_date": "1994-11-02",
  "source_family": "Primary: the TREC-3 paper in which the Okapi team names BM25. Robertson and Zaragoza (A2-SR-15) give the later account of the same lineage.",
  "precise_evidence_location": "Section 1 Introduction (City at TREC-1, City at TREC-2, footnote 1); Section 3.1 Some notation; Section 3.2 Weight functions",
  "method": "System description and experiment report of the City University Okapi system at TREC-3.",
  "limitations": "The file carries no date. The proceedings appeared in 1995; the month is unknown, so the date is set to 1 January 1995. The event date is the TREC-3 conference (November 1994) from my knowledge, not from the file. Text was extracted from PostScript, so typeset formulas are garbled and are described in words. The extraction drops the fi and ff ligatures, shows the dash in TREC-3 as a brace, and shows decimal points as colons; quotes repair these three faults and nothing else. The sentence 'Evaluation results for BM25 with various parameter values are not explicitly given in this paper.' appears in the extracted text at the end of Section 3.2; I could not tell whether it is in the original or an artefact of the file.",
  "provenance": "PostScript downloaded with curl on 2026-11-18, converted with ps2pdf and pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1, City at TREC-1: ranking still used the "probabilistic model of Robertson and Sparck Jones[7] with no account taken of document length or term frequency within document or query."
- Footnote 1: the TREC-1 results would have been worse without truncation of long documents. "This appears to be because the simple weighting scheme tends to favour long documents, particularly FR, few of which are relevant."
- Section 1, City at TREC-2: "the simple inverse collection frequency (ICF) term-weighting scheme was elaborated to embody within-document frequency and document length components, as well as within-query frequency, and a large number of weighting functions were investigated." (line breaks removed.)
- Section 3.2: the base weight is the Robertson-Sparck Jones weight, which "reduces to an inverse collection frequency weight without relevance information (R = r = 0). This is the BM1 function used in TREC-1." (the extracted text shows TREC{1 for TREC-1.)
- Section 3.2: "In the course of investigating variant functions for TREC-3, we in effect combined BM11 and BM15 into a single function BM25, which allowed for a number of variations." (ligatures and hyphenation repaired.)
- Section 3.2: with c = 1, b = 1 gives BM11 and b = 0 gives BM15, and other values of b mix the two (paraphrase; the formula is garbled in the extracted text). The next sentence, quoted whole with the source's own quotation marks: "The basis for BM11 was one of two possible models of document length (the "verbosity" hypothesis, [4]) which might be expected to exaggerate the document length effect; this is the justification for considering the mix." (ligatures repaired.)
- Section 3.2: "The modified weight function seems able to give slightly improved results, at the cost of another parameter to be guessed." and "Values around 0.75 were usually used, sometimes with a higher k1 than for BM11."
- Not shown: the 1994 SIGIR paper by Robertson and Walker on 2-Poisson approximations, which was not read. The TREC-2 functions BM11 and BM15 are recorded from their own paper in A2-SR-16.
