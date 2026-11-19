# A1-SR-13: Sun et al., RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space

```json
{
  "source_identity": "Zhiqing Sun, Zhi-Hong Deng, Jian-Yun Nie, Jian Tang, 'RotatE: Knowledge Graph Embedding by Relational Rotation in Complex Space', ICLR 2019; arXiv:1902.10197v1; https://arxiv.org/abs/1902.10197",
  "author_or_issuing_body": "Sun, Deng (Peking University); Nie (Université de Montréal); Tang (Mila, HEC Montréal)",
  "publisher": "arXiv (Cornell University); conference paper at ICLR 2019",
  "publication_date": "2019-02-26T00:00:00Z",
  "relevant_event_date": "2019-02-26",
  "source_family": "Primary for RotatE. Secondary for its summary of TransE (A1-SR-11), TransH (A1-SR-12), TransR, DistMult, and ComplEx.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 Related Work (Table 1 and the paragraph on relation patterns)",
  "method": "Model design and link prediction experiments. Each relation is a rotation in complex vector space; training uses self-adversarial negative sampling.",
  "limitations": "Shows: the criticism that earlier embeddings each capture only some relation patterns. Does not show: any use of text or any use in retrieval for generation. The criticism of the earlier models is stated by a competing author.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "The success of such a task heavily relies on the ability of modeling and inferring the patterns of (or between) the relations."
- Abstract: "Specifically, the RotatE model defines each relation as a rotation from the source entity to the target entity in the complex vector space."
- Section 2: "For example, TransE represents each relation as a bijection between source entities and target entities, and thus implicitly models inversion and composition of relations, but it cannot model symmetric relations; ComplEx extends DistMult by introducing complex embeddings so as to better model asymmetric relations, but it cannot infer the composition pattern."
- Section 1: "However, none of existing models is capable of modeling and inferring all the above patterns."
