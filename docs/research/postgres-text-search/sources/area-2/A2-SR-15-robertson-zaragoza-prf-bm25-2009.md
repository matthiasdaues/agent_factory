# A2-SR-15: Robertson and Zaragoza, The Probabilistic Relevance Framework: BM25 and Beyond, 2009

```json
{
  "source_identity": "Stephen Robertson and Hugo Zaragoza, 'The Probabilistic Relevance Framework: BM25 and Beyond', Foundations and Trends in Information Retrieval 3(4) (2009) 333-389, doi:10.1561/1500000019; PDF https://www.staff.city.ac.uk/~sbrp622/papers/foundations_bm25_review.pdf",
  "author_or_issuing_body": "Stephen Robertson and Hugo Zaragoza",
  "publisher": "now Publishers (Foundations and Trends in Information Retrieval); PDF hosted on a City, University of London staff page",
  "publication_date": "2009-01-01T00:00:00Z",
  "relevant_event_date": "2009-01-01",
  "source_family": "Primary for the authors' own account and the BM25F formulation as they present it; secondary for the history of BM25 at TREC, which it summarises. Robertson is an author of A2-SR-14 and A2-SR-16, so this is not independent of them.",
  "precise_evidence_location": "Sections 3.4.2 to 3.4.4 (saturation, BM25 precursor), 3.4.5 (document length), 3.5 Uses of BM25, 3.6 Multiple Streams and BM25F, 3.6.1 Basic Idea; references [46] and [48]",
  "method": "Survey monograph that derives the binary independence model, the eliteness (2-Poisson) model, BM25, and BM25F within one framework.",
  "limitations": "Year-only date; set to 1 January 2009. Text came from pdftotext, so formulas are garbled and are described in words. The original BM25F paper (Robertson, Zaragoza, Taylor, CIKM 2004) was not read. The document-length section on scope and verbosity was read in this record; its line numbers come from my extracted text, not the printed pages.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext. Re-verify at the PDF URL above."
}
```

## Evidence

- Section 3.4.2: "We refer to this behaviour as saturation. That is, any one term’s contribution to the document score cannot exceed a saturation point (the asymptotic limit), however, frequently it occurs in the document."
- Section 3.4.4: "Lacking an appropriate generative corpus model from which to derive a convenient formula, the authors of BM25 decided to fit a simple parametric curve to this shape." (ligature repaired.)
- Section 3.4.5, document length: "The verbosity hypothesis suggests that we should simply normalise any observed tf s by dividing by document length. The scope hypothesis, on the other hand, at least in its extreme version, suggests the opposite." and "This in turn suggests that we should apply some kind of soft normalisation."
- After equation 3.15: "This is the classic BM25 term-weighting and document-scoring function."
- Section 3.5: "Concerning the internal parameters, the model provides no guidance on how these should be set. This may be regarded as a limitation of the model." and "values such as 0.5 < b < 0.8 and 1.2 < k1 < 2 are reasonably good in many" circumstances (the sentence runs on to the next page).
- Section 3.6.1: "Given a ranking algorithm or function that can be applied to a piece of undifferentiated text, an obvious practical approach to such a stream structure would be to apply the function separately to each stream, and then combine these in some linear combination (with stream weights)" (ligature repaired; the sentence continues). Section 3.6 then argues that eliteness is a term-document property shared across streams and builds BM25F on that basis (paraphrase).
- Section 3.4.3: "the non-linear, saturating function of tf developed below (also combined with an idf component) has frequently been shown to work better than traditional tf \*idf ."
- Not shown: the BM25 variants after 2009, such as lower-bounded term frequency normalisation.
