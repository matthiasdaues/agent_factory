# A5-SR-11: Christophides et al., End-to-End Entity Resolution for Big Data: A Survey

```json
{
  "source_identity": "Vassilis Christophides, Vasilis Efthymiou, Themis Palpanas, George Papadakis, Kostas Stefanidis, 'End-to-End Entity Resolution for Big Data: A Survey', arXiv:1905.06397v3, ACM Computing Surveys 2020; https://arxiv.org/abs/1905.06397",
  "author_or_issuing_body": "Christophides (ENSEA), Efthymiou (IBM Research), Palpanas (University of Paris), Papadakis (University of Athens), Stefanidis (Tampere University)",
  "publisher": "arXiv; ACM Computing Surveys",
  "publication_date": "2020-08-19T00:00:00Z",
  "relevant_event_date": "1969-01-01",
  "source_family": "Secondary. Survey that cites Fellegi and Sunter 1969 as reference [63] and DeepER and DeepMatcher [52, 122]. It is the only text read here for the 1969 step.",
  "precise_evidence_location": "Section 5.3 Learning-based methods (first paragraph); Section 9.1 Deep Learning",
  "method": "Literature survey of blocking, matching, clustering and incremental entity resolution.",
  "limitations": "Secondary for the Fellegi-Sunter paper: the paper itself (JASA 64(328), 1183-1210, 1969) was found at two course-hosted URLs, but both files returned scanned or corrupt data that could not be read, so the 1969 step rests on this survey. relevant_event_date is the year of Fellegi and Sunter only. The survey is dated August 2020 and does not cover LLM matching. It shows how the authors classify methods; it records no measured error rates.",
  "provenance": "PDF downloaded with curl from https://arxiv.org/pdf/1905.06397 on 2026-11-17 and extracted with pdftotext. Re-verify at the arXiv URL."
}
```

## Evidence

- Section 5.3: "The first probabilistic model for ER [63] used attribute similarities as the dimensions of comparison vectors, each representing the probability that a pair of descriptions match. Following the same conceptual model, a large number of works try to automate the process of learning such probabilities based on manually or automatically generated, or even pre-existing training data." [63] is Fellegi and Sunter 1969.
- Section 9.1: "The latest developments in deep learning have greatly influenced research in ER." DeepER uses word embeddings and recurrent networks; "DeepMatcher [122] extends DeepER by introducing an architecture template for deep learning ER methods" with attribute embedding, similarity representation and a classifier.
- Section 1: ER "aims to identify different descriptions that refer to the same real-world entity ... when unique entity identifiers are not available."
- Reference list entry \[63\]: I. P. Fellegi and A. B. Sunter, A theory for record linkage, JASA 64:1183-1210, 1969.
- Not shown: Newcombe's 1959 matching procedure. A search summary says the 1969 paper's introduction calls its rule 'quite similar to the intuitively appealing approach of Newcombe'; that summary was not checked against the paper text.
