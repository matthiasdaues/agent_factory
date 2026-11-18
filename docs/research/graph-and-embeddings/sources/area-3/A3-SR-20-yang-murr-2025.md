# A3-SR-20: Yang et al., MURR: Model Updating with Regularized Replay for Searching a Document Stream

```json
{
  "source_identity": "Eugene Yang, Nicola Tonellotto, Dawn Lawrie, Sean MacAvaney, James Mayfield, Douglas W. Oard, Scott Miller, 'MURR: Model Updating with Regularized Replay for Searching a Document Stream', arXiv:2504.10250v1; https://arxiv.org/pdf/2504.10250",
  "author_or_issuing_body": "Yang, Lawrie, Mayfield (HLTCOE, Johns Hopkins University); Tonellotto (University of Pisa); MacAvaney (University of Glasgow); Oard (University of Maryland); Miller (ISI, University of Southern California)",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2025-04-14T00:00:00Z",
  "relevant_event_date": "2025-04-14",
  "source_family": "Primary for the MURR update strategy and its statement of the re-indexing problem. Cites backward-compatible training from computer vision, which I read (Shen et al. 2020, arXiv:2003.11942) but did not record.",
  "precise_evidence_location": "Abstract; Section 1 Introduction",
  "method": "Fine-tunes dual-encoder retrieval models on a simulated stream of new topics with regularized replay, so that old document vectors stay searchable without re-encoding.",
  "limitations": "The streams are simulated. The venue was not checked. The paper is about continued fine-tuning of one model; it does not address a switch to an unrelated model.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/2504.10250 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "continued fine-tuning of the language model underlying neural retrieval approaches such as DPR and ColBERT creates incompatibility with previously-encoded documents. Re-encoding and re-indexing all previously-processed documents can be costly."
- Section 1: "Given that these models produce vectors in an arbitrary latent space, an updated model is not guaranteed to be compatible with vectors from another model (though they can be moderately compatible by chance [22]). Therefore, existing approaches either need to use the same model over the lifespan of a dense index (limiting effectiveness) or re-index the entire collection when a new model is trained (a costly endeavor)."
- Shows: the two standard options when a model changes (keep the model, or re-encode everything) and one research attempt to avoid re-encoding.
- Does not show: how vectors are labelled with the model version in a store.
