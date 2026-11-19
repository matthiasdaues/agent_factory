# A2-SR-12: Fox and Shaw, Combination of Multiple Searches, TREC-2

```json
{
  "source_identity": "Edward A. Fox and Joseph A. Shaw, 'Combination of Multiple Searches', The Second Text REtrieval Conference (TREC-2), NIST Special Publication 500-215, pp. 243-252; text at https://trec.nist.gov/pubs/trec2/papers/txt/23.txt",
  "author_or_issuing_body": "Edward A. Fox and Joseph A. Shaw, Department of Computer Science, Virginia Tech",
  "publisher": "National Institute of Standards and Technology (NIST)",
  "publication_date": "1994-03-01T00:00:00Z",
  "relevant_event_date": "1993-08-31",
  "source_family": "Primary: the TREC-2 paper that names the CombSUM and CombMNZ score-fusion formulas. Cited as the standard comparison by Cormack et al. (A2-SR-11).",
  "precise_evidence_location": "Abstract; Table 6 'Formulas for combining similarity values' (page 245); discussion on pages 245 to 246",
  "method": "Fuses the similarity values of five retrieval runs (vector space and P-norm extended Boolean) on TREC collections and compares the fused runs with the single runs.",
  "limitations": "The NIST text file is an OCR rendering with spelling errors (such as 'Compnter'); quotes keep them. The proceedings month is not in the file; March 1994 is my estimate and the day is set to the first. The event date is the TREC-2 conference (August-September 1993) from my knowledge, not from the file. The page numbers come from the running page marks in the text. The quote on the advantages of the chosen methods spans a page break; the page number 246 between its parts is left out. The runs fused are all lexical.",
  "provenance": "Text file downloaded with curl on 2026-11-18 and converted from Latin-1 to UTF-8 with iconv. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "This paper describes one such method that has been shown to increase performance by combining the similarity values from five different retrieval runs using both vector space and P-norm extended boolean retrieval methods." (line breaks and hyphenation removed.)
- Table 6 lists CombMAX, CombMIN, CombSUM, CombANZ, CombMNZ, and CombMED. CombSUM is the sum of the individual similarities; CombMNZ is that sum multiplied by the number of non-zero similarities.
- Page 246: "CombSUM, the summation of the set of similarity values, or, equivalently, the numerical mean of the set of the set of similarity values" and "CombMNZ to provide higher weights to documents retrieved by multiple retrieval methods." (hyphenation removed; the doubled words are in the source.)
- Page 246: "the advantages of those chosen are simplicity, in terms of both execution efficiency and implementation, and generality, in terms of not being specific to a given method or retrieval run." (line breaks removed.)
- Page 245: the authors decided "to weight each of the separate runs equally and not favor any individual run or method" (line breaks and hyphenation removed).
- Not shown: score normalization across systems with different scales; the fused runs share one similarity framework.
