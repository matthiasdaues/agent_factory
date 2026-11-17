# A6-SR-01 — LLMs for Knowledge Graph Construction and Reasoning (Zhu et al., 2023)

```json
{
  "source_identity": "Zhu et al., 'LLMs for Knowledge Graph Construction and Reasoning: Recent Capabilities and Future Opportunities', arXiv:2305.13168, https://arxiv.org/abs/2305.13168",
  "author_or_issuing_body": "Yuqi Zhu, Xiaohan Wang, Jing Chen, Shuofei Qiao, Yixin Ou, Yunzhi Yao, Shumin Deng, Huajun Chen, Ningyu Zhang (Zhejiang University group)",
  "publisher": "arXiv",
  "publication_date": "2023-05-22T00:00:00Z",
  "relevant_event_date": "2023-05-22",
  "source_family": "Primary. Original paper. Lineage: academic preprint, Zhejiang University; later versions to v4 (2024-12-26).",
  "precise_evidence_location": "Abstract; Introduction; Section 3 (AutoKG); statements on evaluation datasets in Section 2.3 (HTML v4).",
  "method": "Empirical evaluation of text-davinci-003, ChatGPT and GPT-4 in zero-shot and one-shot settings on eight datasets (entity and relation extraction, event extraction, link prediction, question answering).",
  "limitations": "Shows that GPT-4 beats ChatGPT on most tasks and is judged better as an inference assistant than as a few-shot extractor. Does not show extraction quality at corpus scale. Samples are small (for example 20 per extraction dataset). The paper states its constructed graphs still need manual validation. The submission date is the v1 date. The venue is not confirmed here.",
  "provenance": "Read on 2026-11-17 through the WebFetch tool, which returns a model-made extract of the page, not the page itself. Re-verify by opening the URL."
}
```

## Evidence

Quotes come from that extract and are limited to short passages.

- Abstract: LLMs, represented by GPT-4, "are more suited as inference assistants rather than few-shot information extractors."
- Section 3: the authors name three open challenges for AutoKG, among them the token limit and "the known propensity of LLMs to generate non-factual information."
- Section 3: "the current results of the constructed knowledge graph still necessitate manual evaluation and validation."
- Section 2.3 and Figure 1 caption: models, eight datasets and sampling; the paper notes "there may be inherent variability in the results due to this sampling approach."
