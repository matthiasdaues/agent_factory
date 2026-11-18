# A4-SR-09: Card et al., The Media Frames Corpus

```json
{
  "source_identity": "Dallas Card, Amber E. Boydstun, Justin H. Gross, Philip Resnik, Noah A. Smith, 'The Media Frames Corpus: Annotations of Frames Across Issues', Proceedings of ACL-IJCNLP 2015 (Short Papers), pp. 438-444; https://aclanthology.org/P15-2072.pdf",
  "author_or_issuing_body": "Card, Smith (Carnegie Mellon University); Boydstun (UC Davis); Gross (UMass Amherst); Resnik (University of Maryland)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2015-07-26T00:00:00Z",
  "relevant_event_date": "2015-07-26",
  "source_family": "Primary for the Media Frames Corpus and its annotation process. Secondary for the 15 framing dimensions of Boydstun et al. (2014), which it adopts, and for Entman (1993, A4-SR-07), which it quotes.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2 What is Framing?; Figure 1 framing dimensions; Section 4 annotation stages; Figure 4 discussion",
  "method": "Trained annotators label several thousand US newspaper articles from 1990-2012 on immigration, smoking, and same-sex marriage with 15 framing dimensions, at span level and as a primary frame per article. Agreement is tracked over three stages.",
  "limitations": "Date set to the first day of the conference (26-31 July 2015). Three US policy issues and 13 US newspapers. The texts are not redistributed; users need a Lexis-Nexis licence. The codebook of Boydstun et al. (2014) was not read. Agreement figures are shown in a figure, not as a single number in the text.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "Past work on framing includes many examples of issue-specific studies based on manual content analysis (...). While such studies reveal much about the range of opinions on an issue, they do not characterize framing at a level of abstraction that allows comparison across social issues."
- Section 1: "These annotations are based on 15 general-purpose metaframes (here called “framing dimensions”) outlined below, which are intended to subsume all specific frames that might be encountered on any issue of public concern."
- Section 2: "In a widely cited definition, Entman (1993) argues that “to frame is to select some aspects of a perceived reality and make them more salient in a communicating text, in such a way as to promote problem definition, causal interpretation, moral evaluation, and/or treatment recommendation for the item described.”"
- Section 1: "A degree of subjectivity in framing analysis is unavoidable. While some variation in annotations is due to mistakes and misunderstandings by annotators (and is to be minimized), much variation is due to valid differences in interpretation (and is therefore properly preserved in the coding process)."
- Section 4: "Disagreements continue to arise, however, reflecting the reality that the same article can cue different frames more strongly for different annotators."
- Figure 4 discussion: "Although we never obtain perfect agreement, this is not surprising, given that the same sentences can and do cue multiple types of framing".
- Shows: the move from issue-specific codebooks to a fixed set of generic framing dimensions, motivated by the lack of comparison across issues. It is a method for labelling the frame of a single article.
- Does not show: a method that compares the frame of a downstream article with the frame of its source.
