# A3-SR-08: Muennighoff et al., MTEB: Massive Text Embedding Benchmark

```json
{
  "source_identity": "Niklas Muennighoff, Nouamane Tazi, Loic Magne, Nils Reimers, 'MTEB: Massive Text Embedding Benchmark', arXiv:2210.07316v3; https://arxiv.org/pdf/2210.07316",
  "author_or_issuing_body": "Muennighoff, Tazi, Magne (Hugging Face); Reimers (cohere.ai)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2022-10-01T00:00:00Z",
  "relevant_event_date": "2022-10-01",
  "source_family": "Primary for MTEB and its own list of limitations. Includes BEIR (A3-SR-07) and the STS tasks (A3-SR-02) as parts.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 3 task descriptions (Pair Classification); Appendix Limitations of MTEB",
  "method": "Benchmarks 33 embedding models on 8 task types over 58 datasets and 112 languages with one evaluation code base.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v3 of 19 March 2023. The text extraction places the limitations list among the appendix tables; items 1 and 2 were read in order, items 3 and 4 only by heading. The leaderboard changes over time; this record covers the paper only.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2210.07316 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "It is unclear whether state-of-the-art embeddings on semantic textual similarity (STS) can be equally well applied to other tasks like clustering or reranking."
- Abstract: "We find that no particular text embedding method dominates across all tasks."
- Section 1: "SimCSE (Gao et al., 2021b) or SBERT (Reimers and Gurevych, 2019) solely evaluate on STS and classification tasks, leaving open questions about the transferability of the embedding models to search or clustering tasks. STS is known to poorly correlate with other real-world use cases (Neelakantan et al., 2022; Wang et al., 2021)."
- Section 3: "Pair Classification A pair of text inputs is provided and a label needs to be assigned. Labels are typically binary variables denoting duplicate or paraphrase pairs."
- Appendix, limitation 1: "The longest datasets in MTEB have a few hundred words, and longer text sizes could be relevant for use cases like retrieval."
- Appendix, limitation 2: "MTEB average scores, which are computed over all datasets, are biased towards tasks with many datasets, notably retrieval, classification and clustering."
- Shows: the criticism of STS-only evaluation, paraphrase and duplicate detection as a task type, and the authors' own limits on length and task balance.
- Does not show: claim matching or text reuse as separate tasks.
