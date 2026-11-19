# A1-SR-15: Ji et al., A Survey on Knowledge Graphs: Representation, Acquisition and Applications

```json
{
  "source_identity": "Shaoxiong Ji, Shirui Pan, Erik Cambria, Pekka Marttinen, Philip S. Yu, 'A Survey on Knowledge Graphs: Representation, Acquisition and Applications', IEEE Transactions on Neural Networks and Learning Systems (2021); arXiv:2002.00388v4; https://arxiv.org/abs/2002.00388",
  "author_or_issuing_body": "Ji, Marttinen (Aalto University); Pan (Monash University); Cambria (Nanyang Technological University); Yu (University of Illinois at Chicago)",
  "publisher": "arXiv (Cornell University); journal version in IEEE Transactions on Neural Networks and Learning Systems",
  "publication_date": "2020-02-02T00:00:00Z",
  "relevant_event_date": "2020-02-02",
  "source_family": "Secondary. Survey of knowledge graph representation learning. Independent of the primary embedding papers A1-SR-11 to A1-SR-14.",
  "precise_evidence_location": "Abstract; Section III.D Embedding with Auxiliary Information, item 1 Textual Description",
  "method": "Literature survey with a taxonomy of knowledge graph embeddings by representation space, scoring function, encoding model, and auxiliary information.",
  "limitations": "Date is arXiv v1; the text read is v4 of 1 April 2021. The two-column PDF extracted with mixed columns; the quotes were checked against a crop of the left column (pdftotext -x 0 -W 306, pages 6 to 8). Predates retrieval-augmented generation over graphs. Shows: that joining structure and text in one embedding space is a named challenge. Does not show: retrieval use or update behaviour.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. A second extraction with pdftotext -layout was used to separate the columns. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Knowledge graph embedding is organized from four aspects of representation space, scoring function, encoding models, and auxiliary information."
- Section III.D: "Multi-modal embedding incorporates external information such as text descriptions, type constraints, relational paths, and visual information, with a knowledge graph itself to facilitate more effective knowledge representation."
- Section III.D.1: "The challenge of KRL with textual description is to embed both structured knowledge and unstructured textual information in the same space."
- Section III.D.1, paraphrase: DKRL extends TransE to learn entity representations from descriptions with a convolutional encoder.
