# A2-SR-12: Schlichtkrull et al., AVeriTeC: A Dataset for Real-world Claim Verification with Evidence from the Web

```json
{
  "source_identity": "Michael Schlichtkrull, Zhijiang Guo, Andreas Vlachos, 'AVeriTeC: A Dataset for Real-world Claim Verification with Evidence from the Web', NeurIPS 2023 Datasets and Benchmarks Track; arXiv:2305.13117 v3",
  "author_or_issuing_body": "Michael Schlichtkrull, Zhijiang Guo, Andreas Vlachos (University of Cambridge)",
  "publisher": "NeurIPS 2023 proceedings; preprint on arXiv",
  "publication_date": "2023-05-01T00:00:00Z",
  "relevant_event_date": "2023-12-10",
  "source_family": "Primary: the Cambridge fact-verification lineage that also produced A2-SR-03 and A2-SR-11. Criticises FEVER-style datasets. Claims come through the Google Fact Check Claim Search API, which reads ClaimReview (A2-SR-14).",
  "precise_evidence_location": "Abstract; Section 1 Introduction (criticism of earlier datasets and the three issues: context dependence, evidence insufficiency, temporal leaks)",
  "method": "Collects 4,568 real-world claims from 50 fact-checking organisations and annotates question-answer evidence from the open web and textual justifications in several rounds.",
  "limitations": "publication_date is set to May 2023 from the arXiv number 2305 (month only); the v3 copy read has no date in the passages extracted. relevant_event_date stands for the NeurIPS 2023 conference and is approximate.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/2305.13117."
}
```

## Evidence

- Abstract: "Existing datasets for automated fact-checking have substantial limitations, such as relying on artificial claims, lacking annotations for evidence and intermediate reasoning, or including evidence published after the claim."
- Section 1: "Many datasets (for example, Thorne et al. [2018], Schuster et al. [2021], Aly et al. [2021]) contain purpose-made claims derived from sources such as Wikipedia, and are thus unlike real-world claims checked by journalists."
- Section 1: "We address (3) by restricting annotators to evidence documents published before the claim, and by ordering our training, development, and test splits temporally."
- Section 1: "With the increasing reliance on large pretrained language models, temporal ordering provides an additional benefit: if the training data for the language model is cut off before the temporal start of the test set, leaks from pretraining cannot occur either."
- Shows: the reformulation of verification over real-world claims with evidence dated before the claim, driven by named criticism of earlier datasets. Does not show: system results beyond a baseline. The 2024 AVeriTeC shared task (arXiv 2410.23850) reports that "Most systems employed an LLM-based question generation strategy"; that paper was read only in part.
