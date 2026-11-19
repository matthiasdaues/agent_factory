# A3-SR-12: Zhou et al., Length-Induced Embedding Collapse in PLM-based Models

```json
{
  "source_identity": "Yuqi Zhou, Sunhao Dai, Zhanshuo Cao, Xiao Zhang, Jun Xu, 'Length-Induced Embedding Collapse in PLM-based Models', arXiv:2410.24200v2; https://arxiv.org/pdf/2410.24200",
  "author_or_issuing_body": "Zhou, Dai, Cao, Zhang, Xu (Gaoling School of Artificial Intelligence, Renmin University of China)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2024-10-01T00:00:00Z",
  "relevant_event_date": "2024-10-01",
  "source_family": "Primary for the length collapse finding. Uses MTEB (A3-SR-08) for evaluation.",
  "precise_evidence_location": "Abstract",
  "method": "Theoretical analysis of self-attention as a low-pass filter and experiments on embedding distributions of texts of different lengths; proposes a temperature scaling fix (TempScale).",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The version read is v2 of 10 June 2025; the venue was not checked. Only the abstract and the introduction were read closely. The reported gains are below 1.1 percentage points.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2410.24200 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Text embeddings from PLM-based models enable a wide range of applications, yet their performance often degrades on longer texts."
- Abstract: "we introduce a phenomenon we call Length Collapse, where embeddings of longer texts tend to cluster together. This clustering results in a distributional inconsistency between the embeddings of short and long texts."
- Abstract: "This approach leads to performance improvements of 0.94% on MTEB and 1.10% on LongEmbed"
- Shows: text length as a limit of embedding similarity: long texts drift toward each other.
- Does not show: a threshold length per model.
