# A5-SR-09: Hogan et al., Knowledge Graphs, Section 3.3 Context

```json
{
  "source_identity": "Aidan Hogan et al., 'Knowledge Graphs', ACM Computing Surveys 54(4), 2021; arXiv:2003.02320v6, https://arxiv.org/abs/2003.02320",
  "author_or_issuing_body": "Aidan Hogan, Eva Blomqvist, Michael Cochez, Claudia d'Amato, Gerard de Melo, Claudio Gutierrez, and twelve further authors",
  "publisher": "ACM Computing Surveys; arXiv preprint",
  "publication_date": "2021-09-11T00:00:00Z",
  "relevant_event_date": "2021-09-11",
  "source_family": "Secondary. Peer-reviewed survey. It cites Temporal RDF (A5-SR-06, as [210]), reification [111], singleton properties [383] and RDF* [218]. One author (Gutierrez) is an author of A5-SR-06.",
  "precise_evidence_location": "Section 3.3 Context, subsections 3.3.1 Direct representation, 3.3.2 Reification, 3.3.3 Higher-arity representation, and the annotation discussion with Figure 20",
  "method": "Literature survey. It compares ways to attach temporal context to an edge.",
  "limitations": "Survey; it reports what papers propose, not usage data. Covers temporal context as one case of context, so it does not discuss bitemporal models. The statement about which representation is 'most flexible' is the authors' judgement. Date is that of arXiv version 6; the ACM publication is dated 2021.",
  "provenance": "PDF downloaded with curl from https://arxiv.org/pdf/2003.02320 on 2026-11-17 and extracted with pdftotext. Re-verify at the arXiv URL, text lines near 'Context'."
}
```

## Evidence

- Section 3.3.1: temporal context can be "data no different from other data", for example the Time Ontology.
- Section 3.3.2: reification forms for temporal context: RDF reification, n-ary relations, singleton properties. "In general, a reified edge does not assert the edge it reifies."
- Section 3.3.3: higher-arity forms: a named graph, a property graph edge attribute, or RDF\*. "Amongst these options, the most flexible is the named graph representation, where we can assign context to multiple edges at once".
- Annotation discussion after 3.3.3 (Figure 20): "Temporal RDF [210] allows for annotating edges with time intervals".
- Not shown: which representation practitioners prefer, or any measurement of query cost.
