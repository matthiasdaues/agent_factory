# A4-SR-17: Verma and Jaidka, The MediaSpin Dataset: Post-Publication News Headline Edits Annotated for Media Bias

```json
{
  "source_identity": "Preetika Verma, Kokil Jaidka, 'The MediaSpin Dataset: Post-Publication News Headline Edits Annotated for Media Bias', arXiv:2412.02271v3 (accepted at AAAI ICWSM 2026); https://arxiv.org/pdf/2412.02271v3; dataset DOI 10.7910/DVN/MOCQTZ",
  "author_or_issuing_body": "Preetika Verma (National University of Singapore; Carnegie Mellon University), Kokil Jaidka (National University of Singapore)",
  "publisher": "arXiv (Cornell University); the peer-reviewed version appears in the Proceedings of the International AAAI Conference on Web and Social Media, vol. 20",
  "publication_date": "2026-03-22T00:00:00Z",
  "relevant_event_date": "2024-12-03",
  "source_family": "Primary for the MediaSpin dataset, its 13-category bias annotation of headline edits, and its validation. Secondary for NewsEdits (Spangher et al. 2022), from which the headline pairs come, and for the media-bias taxonomies it adopts (Spinde et al. 2023; Hamborg, Donnay and Gipp 2020).",
  "precise_evidence_location": "Abstract; Introduction; Related Work, subsections 'Framing and Media Bias in News Texts' and 'Dynamic Editing, Revision Histories, and Editorial Intent'; 'Data Collection and Annotation Process'; 'Human Validation'; Figure 1 (annotation prompt); 'Dataset Limitations'",
  "method": "Takes original and edited headline pairs from the NewsEdits revision histories of five English-language outlets. Lists the added and removed words. GPT-3.5-turbo labels each pair for 13 bias types as added, removed, or not relevant. Two co-authors check 509 sampled labels.",
  "limitations": "Read from arXiv v3 (22 March 2026), not from the ICWSM proceedings PDF; the latest arXiv version is v5 (15 May 2026). Spot checks of v5 found the core passages unchanged except the intent passage, which v5 rewords. publication_date is the v3 revision date. relevant_event_date is the first arXiv posting; the paper does not state the date range of the headlines. One LLM produces the labels. Only Anglophone outlets. All pairs are revisions within one outlet.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from arxiv.org (v3 and v5) and extracted with pdftotext. An earlier attempt on the ojs.aaai.org PDF link returned an HTML page. Re-verify at the URL above or at https://doi.org/10.1609/icwsm.v20i1.42794."
}
```

## Evidence

- Abstract: "We present MediaSpin, a large-scale language resource capturing how major news outlets modify headlines after publication".
- Abstract: "The dataset contains 78,910 headline pairs annotated for 13 types of media bias".
- Introduction: "This phenomenon of dynamic news framing, where headlines are revised post-publication, remains underexplored in prior research."
- Related Work: "Research gap. Nearly all computational approaches analyze final published headlines or articles. Although framing is theorized as the outcome of iterative editorial decisions, current corpora do not capture the revision process".
- Related Work: "Research gap. Existing revision datasets do not annotate what types of bias edits introduce or remove."
- Related Work: "Computational systems such as Newsalyze model these differences by identifying sentiment and frame-bearing lexical variation across outlets (Hamborg 2023)." This is the paper's only pointer to cross-outlet comparison, and it is a citation, not its own method.
- Data Collection: "We selected headline edit pairs from the NewsEdits dataset for five English language media outlets".
- Figure 1 prompt: "You will be given a news headline and an edited version of the same headline."
- Figure 1 prompt: "Spin (e.g., changing "protest" to "riot")". The inner quotes are the paper's own.
- Human Validation: "The overall inter-annotator agreement (pairwise percentage agreement) was 84.9%, with a corresponding Cohen’s κ of 0.67".
- Human Validation: "The most common error type was directional—GPT-3.5-turbo indicated an addition of bias when the edit actually removed bias."
- Dataset Limitations (v3): "MediaSpin captures what changed, not why it changed."
- Shows: a pairwise method for a change of spin or frame between two versions of a headline. Each pair gets a label per bias type and a direction, added or removed. The direction is the part the LLM gets wrong most often.
- Does not show: a change of frame between a source text and a downstream version by another outlet. Both headlines in every pair come from the same article of the same outlet. The paper compares only headlines, not article bodies, and it uses no frame scheme such as the Media Frames Corpus (A4-SR-09).
