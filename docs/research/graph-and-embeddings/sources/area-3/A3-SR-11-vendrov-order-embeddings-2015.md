# A3-SR-11: Vendrov et al., Order-Embeddings of Images and Language

```json
{
  "source_identity": "Ivan Vendrov, Ryan Kiros, Sanja Fidler, Raquel Urtasun, 'Order-Embeddings of Images and Language', ICLR 2016, arXiv:1511.06361v6; https://arxiv.org/pdf/1511.06361",
  "author_or_issuing_body": "Vendrov, Kiros, Fidler, Urtasun (University of Toronto)",
  "publisher": "arXiv (Cornell University); the PDF header states publication as an ICLR 2016 conference paper",
  "publication_date": "2015-11-01T00:00:00Z",
  "relevant_event_date": "2015-11-01",
  "source_family": "Primary for order embeddings and their argument against symmetric distances for entailment.",
  "precise_evidence_location": "Abstract; Section 1 Introduction",
  "method": "Learns embeddings in which a partial order, not a distance, encodes hypernymy, textual entailment, and caption-image relations; evaluates on hypernym prediction, caption-image retrieval, and SNLI.",
  "limitations": "publication_date is the first day of the month of the first arXiv version, taken from the arXiv identifier; the exact day was not checked. The paper predates BERT, and its models are not the ones used today. It argues that symmetric distances introduce systematic error; it does not measure that error for modern sentence encoders.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/1511.06361 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Hypernymy, textual entailment, and image captioning can be seen as special cases of a single visual-semantic hierarchy over words, sentences, and images."
- Section 1: "A symmetric distance measure such as Euclidean or cosine distance is typically used. Since the visual-semantic hierarchy is an antisymmetric relation, we expect this approach to introduce systematic model error."
- Section 1: "Notably, no existing approach directly imposes the transitivity and antisymmetry of the partial order"
- Shows: the argument that cosine similarity cannot express the direction of entailment.
- Does not show: whether current embedding models still lose direction in practice. I found no recent measurement; see the gaps in the area index.
