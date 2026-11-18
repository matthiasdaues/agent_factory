# A2-SR-13: Bruch, Gai, Ingber, An Analysis of Fusion Functions for Hybrid Retrieval, 2023

```json
{
  "source_identity": "Sebastian Bruch, Siyu Gai, Amir Ingber, 'An Analysis of Fusion Functions for Hybrid Retrieval', arXiv:2210.11934v2 (4 May 2023), published in ACM Transactions on Information Systems; https://arxiv.org/abs/2210.11934",
  "author_or_issuing_body": "Sebastian Bruch (Pinecone), Siyu Gai (University of California, Berkeley), Amir Ingber (Pinecone)",
  "publisher": "arXiv (preprint server, Cornell University); journal version ACM",
  "publication_date": "2023-05-04T00:00:00Z",
  "relevant_event_date": "2022-10-21",
  "source_family": "Primary for its own analysis and experiments. Secondary for the claims of Chen et al. 2022 (its reference [5], zero-shot hybrid retrieval with RRF), which it summarises. Its RRF definition follows Cormack et al. (A2-SR-11).",
  "precise_evidence_location": "Abstract; Section 1 Introduction (pages 1 to 3, footnote 1); Section 5 opening and 5.1 Effect of Parameters (pages 15 to 17)",
  "method": "Theoretical analysis of convex combination of normalized scores and of RRF, plus experiments on in-domain and out-of-domain retrieval datasets with lexical (BM25) and semantic (dense embedding) retrievers, measured by NDCG and recall.",
  "limitations": "Two authors work for a vector database vendor. The paper studies retrieval quality, not SQL or PostgreSQL. The journal version was not read; the volume and pages are not recorded. relevant_event_date is the v1 arXiv date from my knowledge of the listing and was not checked. Chen et al. 2022 was not read.",
  "provenance": "PDF of v2 downloaded with curl from https://arxiv.org/pdf/2210.11934 on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Contrary to existing studies, we find RRF to be sensitive to its parameters; that the learning of a CC fusion is generally agnostic to the choice of score normalization; that CC outperforms RRF in in-domain and out-of-domain settings; and finally, that CC is sample efficient, requiring only a small set of training examples to tune its only parameter to a target domain." CC stands for convex combination.
- Section 1: the convex combination is "𝑓Convex = 𝛼 𝑓Sem + (1 − 𝛼) 𝑓Lex where 0 ≤ 𝛼 ≤ 1", and "Because lexical scores (such as BM25) and semantic scores (such as dot product) may be unbounded, often they are normalized with min-max scaling".
- Section 1, on the earlier position: "A recent study [5] argues that convex combination is sensitive to its parameter 𝛼 and the choice of score normalization." and "They claim and show empirically, instead, that Reciprocal Rank Fusion (RRF) [6] may be a more suitable fusion as it is non-parametric and may be utilized in a zero-shot manner."
- Section 1: "We then intuit that, because RRF is a function of ranks, it disregards the distribution of scores and, as such, discards useful information."
- Section 5: "Our results show that hybrid retrieval using RRF outperforms pure-lexical and pure-semantic retrieval on most datasets." and "Contrary to [5], however, we find that TM2C2 significantly outperforms RRF on all datasets in terms of NDCG, and does generally better in terms of Recall." TM2C2 is their convex combination with theoretical min-max normalization.
- Section 5: "We note that, we set RRF’s 𝜂 to 60 per [5] but tuned TM2C2’s 𝛼 on the validation set of the in-domain datasets and found that 𝛼 = 0.8 works well for the three datasets."
- Not shown: an SQL formulation, and how to obtain the theoretical minimum of a BM25 score inside PostgreSQL.
