# A2-SR-10: Kazemi et al., Claim Matching Beyond English to Scale Global Fact-Checking

```json
{
  "source_identity": "Ashkan Kazemi, Kiran Garimella, Devin Gaffney, Scott A. Hale, 'Claim Matching Beyond English to Scale Global Fact-Checking', ACL-IJCNLP 2021; arXiv:2106.00853",
  "author_or_issuing_body": "Ashkan Kazemi (University of Michigan, Meedan); Kiran Garimella (MIT); Devin Gaffney (Meedan); Scott A. Hale (University of Oxford, Meedan)",
  "publisher": "Association for Computational Linguistics; preprint on arXiv",
  "publication_date": "2021-06-01T00:00:00Z",
  "relevant_event_date": "2021-08-01",
  "source_family": "Primary: the Meedan claim-matching lineage, built on WhatsApp tipline data. Criticises A2-SR-07 and reuses the claim definition of A2-SR-05.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (datasets); Section 2 Related work (Claim matching); Section 3 annotation task 1",
  "method": "Annotates WhatsApp tipline and public-group messages in five languages for claim-like statements and for pairwise claim similarity, then trains a multilingual embedding model by knowledge distillation.",
  "limitations": "relevant_event_date stands for ACL-IJCNLP 2021 (month only) and is approximate. The data come from tiplines run with fact-checkers in India and may not carry over to other regions.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/2106.00853."
}
```

## Evidence

- Abstract: "We define claim matching as the task of identifying pairs of textual messages containing claims that can be served with one fact-check."
- Section 1: messages "have been triple annotated for containing ‘claim-like statements’ following the definition proposed by fact-checkers in Konstantinovskiy et al. (2020)."
- Section 2: "these projects only focus on English data that mainly cover U.S. politics and at least one of the matching pairs is a claim from a fact-check report."
- Section 2: "the data collection process used in Shaar et al. (2020) might not necessarily capture all possible matches for a claim, since the dataset is constructed by including only the claims mentioned in one fact-check report and not all previous occurrences."
- Shows: claim matching widened from input-to-verified-claim ranking to any pair of messages one fact-check can serve, across languages. Does not show: matching of images or video.
