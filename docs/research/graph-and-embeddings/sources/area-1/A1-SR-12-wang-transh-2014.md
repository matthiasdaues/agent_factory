# A1-SR-12: Wang et al., Knowledge Graph Embedding by Translating on Hyperplanes (TransH)

```json
{
  "source_identity": "Zhen Wang, Jianwen Zhang, Jianlin Feng, Zheng Chen, 'Knowledge Graph Embedding by Translating on Hyperplanes', Proceedings of the Twenty-Eighth AAAI Conference on Artificial Intelligence (2014); https://ojs.aaai.org/index.php/AAAI/article/view/8870",
  "author_or_issuing_body": "Wang, Feng (Sun Yat-sen University); Zhang, Chen (Microsoft Research)",
  "publisher": "AAAI Press",
  "publication_date": "2014-01-01T00:00:00Z",
  "relevant_event_date": "2014-01-01",
  "source_family": "Primary. First successor and critic of TransE (A1-SR-11) in the translational line.",
  "precise_evidence_location": "Abstract; Introduction (analysis of TransE flaws and the TransH proposal)",
  "method": "Model design and experiments on link prediction, triple classification, and fact extraction on WordNet and Freebase.",
  "limitations": "Year-only date; set to 1 January 2014. TransR, DistMult, and ComplEx, which follow in the lineage, were not read in full text; RotatE (A1-SR-13) summarises them. Shows: the criticism of TransE on relation mapping properties. Does not show: any use with text or retrieval.",
  "provenance": "PDF downloaded with curl from ojs.aaai.org (article/download/8870/8729) on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We discuss some mapping properties of relations which should be considered in embedding, such as reflexive, one-to-many, many-to-one, and many-to-many. We note that TransE does not do well in dealing with these properties."
- Abstract: "To make a good trade-off between model capacity and efficiency, in this paper we propose TransH which models a relation as a hyperplane together with a translation operation on it."
- Introduction: "Some advanced models with more free parameters are capable of preserving these mapping properties, however, the model complexity and running time is significantly increased accordingly."
