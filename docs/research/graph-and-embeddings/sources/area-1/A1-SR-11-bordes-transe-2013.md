# A1-SR-11: Bordes et al., Translating Embeddings for Modeling Multi-relational Data (TransE)

```json
{
  "source_identity": "Antoine Bordes, Nicolas Usunier, Alberto Garcia-Duran, Jason Weston, Oksana Yakhnenko, 'Translating Embeddings for Modeling Multi-relational Data', NeurIPS 2013; https://papers.neurips.cc/paper/5071-translating-embeddings-for-modeling-multi-relational-data.pdf",
  "author_or_issuing_body": "Bordes, Usunier, Garcia-Duran (Université de Technologie de Compiègne, CNRS); Weston, Yakhnenko (Google)",
  "publisher": "Advances in Neural Information Processing Systems 26 (NeurIPS proceedings)",
  "publication_date": "2013-01-01T00:00:00Z",
  "relevant_event_date": "2013-01-01",
  "source_family": "Primary. Origin of the translational knowledge graph embedding. Criticised by TransH (A1-SR-12) and RotatE (A1-SR-13).",
  "precise_evidence_location": "Abstract; Section 1 Introduction (relationships as translations); Section 5 Conclusion and future work",
  "method": "Model design and link prediction experiments on WordNet and Freebase subsets. Entities are vectors; each relation is a translation vector; training ranks true triples above corrupted ones.",
  "limitations": "Year-only date; set to 1 January 2013. Shows: a structure embedding learned only from the triples, with no text input. Does not show: use in retrieval for text generation; that use comes later. The authors state they do not know whether all relation types fit the model.",
  "provenance": "PDF downloaded with curl from papers.neurips.cc on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Hence, we propose TransE, a method which models relationships by interpreting them as translations operating on the low-dimensional embeddings of the entities."
- Section 1: "In TransE, relationships are represented as translations in the embedding space: if (h, `, t) holds, then the embedding of the tail entity t should be close to the embedding of the head entity h plus some vector that depends on the relationship `." Note: the backquote stands for the script letter l in the PDF.
- Section 5: "Although it remains unclear to us if all relationship types can be modeled adequately by our approach, by breaking down the evaluation into categories (1-to-1, 1-to-Many, . . . ) it appears to be performing well compared to other approaches across all settings."
- Section 5: "Combining KBs with text as in [2] is another important direction where our approach could prove useful."
