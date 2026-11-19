# A2-SR-15: Hugging Face metadata of qmd's default models

```json
{
  "source_identity": "Hugging Face model API entries ggml-org/embeddinggemma-300M-GGUF, google/embeddinggemma-300m, ggml-org/Qwen3-Reranker-0.6B-Q8_0-GGUF, Qwen/Qwen3-Reranker-0.6B, tobil/qmd-query-expansion-1.7B-gguf, at https://huggingface.co/api/models/<id>",
  "author_or_issuing_body": "Google; Alibaba Qwen team; ggml-org; tobil (qmd owner)",
  "publisher": "Hugging Face",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2026-01-25",
  "source_family": "Primary: model metadata on the hosting registry. The three model URIs come from qmd's src/llm.ts as quoted in A2-SR-02; the metadata itself is independent of the tobi/qmd repository.",
  "precise_evidence_location": "API fields id, createdAt, lastModified, gated, tags (license and base_model), cardData.license, cardData.base_model",
  "method": "Read with curl and a short Python JSON print on 2026-11-18.",
  "limitations": "Registry tags only; model cards and licence texts were not read. Whether the Gemma licence counts as open source was not checked against the OSI list. relevant_event_date is the creation date of the qmd query expansion model. publication_date is the read date.",
  "provenance": "curl https://huggingface.co/api/models/<id> on 2026-11-18. Re-verify at the same URLs."
}
```

## Evidence

- ggml-org/embeddinggemma-300M-GGUF: base_model google/embeddinggemma-300m; gated false; no licence tag on the GGUF entry. google/embeddinggemma-300m: licence tag "license:gemma"; gated "manual".
- ggml-org/Qwen3-Reranker-0.6B-Q8_0-GGUF and Qwen/Qwen3-Reranker-0.6B: licence tag "license:apache-2.0"; gated false.
- tobil/qmd-query-expansion-1.7B-gguf: base_model Qwen/Qwen3-1.7B; licence tag "license:mit"; created 2026-01-25; last modified 2026-01-29.
- Shows: the licence each default model carries on the registry and which base model it derives from. Does not show: model quality, training data, or the licence of the GRPO training data in the repository's finetune/ folder.
