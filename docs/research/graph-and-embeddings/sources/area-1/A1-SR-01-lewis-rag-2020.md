# A1-SR-01: Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

```json
{
  "source_identity": "Patrick Lewis et al., 'Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks', NeurIPS 2020; arXiv:2005.11401v4; https://arxiv.org/abs/2005.11401",
  "author_or_issuing_body": "Lewis, Perez, Piktus, Petroni, Karpukhin, Goyal, Küttler, Lewis, Yih, Rocktäschel, Riedel, Kiela (Facebook AI Research, University College London, New York University)",
  "publisher": "arXiv (Cornell University); conference version in Advances in Neural Information Processing Systems 33",
  "publication_date": "2020-05-22T00:00:00Z",
  "relevant_event_date": "2020-05-22",
  "source_family": "Primary. Origin of the term retrieval-augmented generation (RAG). Builds on REALM and ORQA, which it cites. Starting point of the graph retrieval lineage in A1-SR-02 to A1-SR-10.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2.4 Training; Section 3 Experiments (Wikipedia chunking); Section 4.5 Index hot-swapping paragraph; Appendix on parameters",
  "method": "Model design and experiments. A pre-trained seq2seq generator is joined to a dense vector index of Wikipedia passages through a pre-trained neural retriever, then fine-tuned and evaluated on question answering and generation tasks.",
  "limitations": "Date is arXiv v1; the text read is v4 of 12 April 2021. The design has no graph. It embeds text spans (100-word chunks) only. The hot-swap test replaces the whole index; it does not show an update of single passages. Shows: the vector-only baseline that later graph designs react to. Does not show: any graph structure, any partial index update, or any consistency mechanism between two stores.",
  "provenance": "PDF downloaded with curl from arXiv on 2026-11-18 and extracted with pdftotext; quotes copied from the extracted text, with line breaks and hyphenation joined. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "We introduce RAG models where the parametric memory is a pre-trained seq2seq model and the non-parametric memory is a dense vector index of Wikipedia, accessed with a pre-trained neural retriever."
- Abstract: "Additionally, providing provenance for their decisions and updating their world knowledge remain open research problems."
- Section 3: "Each Wikipedia article is split into disjoint 100-word chunks, to make a total of 21M documents." Note: the embedded unit is a text span.
- Section 2.4: "Updating the document encoder BERTd during training is costly as it requires the document index to be periodically updated as REALM does during pre-training [20]. We do not find this step necessary for strong performance, and keep the document encoder (and index) fixed, only fine-tuning the query encoder BERTq and the BART generator."
- Section 4.5: "Index hot-swapping An advantage of non-parametric memory models like RAG is that knowledge can be easily updated at test time."
- Section 4.5: "This shows we can update RAG’s world knowledge by simply replacing its non-parametric memory." Note: the update is a whole-index replacement (December 2016 dump against December 2018 dump).
- Not shown: any graph, any per-document update, or any deletion path.
