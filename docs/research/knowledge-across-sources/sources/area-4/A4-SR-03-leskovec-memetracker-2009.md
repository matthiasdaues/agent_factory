# A4-SR-03: Leskovec, Backstrom, Kleinberg, Meme-tracking and the Dynamics of the News Cycle

```json
{
  "source_identity": "Jure Leskovec, Lars Backstrom, Jon Kleinberg, 'Meme-tracking and the Dynamics of the News Cycle', KDD '09, Paris; https://www.cs.cornell.edu/home/kleinber/kdd09-quotes.pdf",
  "author_or_issuing_body": "Leskovec (Stanford University), Backstrom and Kleinberg (Cornell University)",
  "publisher": "ACM SIGKDD; PDF hosted by Cornell University",
  "publication_date": "2009-06-01T00:00:00Z",
  "relevant_event_date": "2008-08-01",
  "source_family": "Primary for the Memetracker phrase-clustering method and its news-cycle results.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 Algorithms for clustering mutational variants of phrases, the phrase graph paragraph; Figure 1",
  "method": "Collects 90 million news and blog articles from 1.6 million sites over the last three months of the 2008 US presidential election. Extracts quoted phrases, links a shorter phrase to a longer one when it is an approximate excerpt, and partitions the resulting graph into clusters of variants.",
  "limitations": "Month-only date; set to 1 June 2009, approximate for KDD 2009 (late June). The PDF is the authors' copy with a placeholder ACM copyright line. The method tracks quoted phrases only, not paraphrased claims. Inclusion uses word edit distance of at most one or a 10-word overlap, so a reworded quote outside these bounds is missed.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from Jon Kleinberg's Cornell page and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We develop a framework for tracking short, distinctive phrases that travel relatively intact through on-line text; developing scalable algorithms for clustering textual variants of such phrases, we identify a broad class of memes that exhibit wide spread and rich variation on a daily basis."
- Section 1: "we find that while they remain recognizable as they appear in text over time, they also undergo significant mutation."
- Section 2: "The dominant way in which one finds textual variants in our quote data is excerpting — when phrase p is a contiguous subsequence of the words in phrase q."
- Section 2: "p has directed edit distance to q — treating words as tokens — that is less than a small threshold δ (δ = 1 in our implementation) or there is at least a k-word consecutive overlap between the phrases".
- Abstract: "we observe a typical lag of 2.5 hours between the peaks of attention to a phrase in the news media and in blogs respectively".
- Shows: a method for verbatim and slightly altered propagation of quoted phrases across outlets, with excerpting as the main kind of variation.
- Does not show: whether a variant changes the meaning, the frame, or the stance of the quote. It also does not identify which outlet copied from which.
