# A3-SR-22: Ryant et al., The Second DIHARD Diarization Challenge (2019)

```json
{
  "source_identity": "Neville Ryant, Kenneth Church, Christopher Cieri, Alejandrina Cristia, Jun Du, Sriram Ganapathy, Mark Liberman, 'The Second DIHARD Diarization Challenge: Dataset, task, and baselines', arXiv:1906.07839v1 (Interspeech 2019); https://arxiv.org/pdf/1906.07839",
  "author_or_issuing_body": "Ryant, Cieri, Liberman (Linguistic Data Consortium, University of Pennsylvania); Church (Baidu Research); Cristia (ENS/CNRS); Du (USTC); Ganapathy (Indian Institute of Science)",
  "publisher": "arXiv (Cornell University); also published at Interspeech 2019",
  "publication_date": "2019-06-18T00:00:00Z",
  "relevant_event_date": "2019-06-18",
  "source_family": "Primary for the DIHARD II task, metrics, and the JER definition. Secondary for the NIST Rich Transcription evaluations (2002 to 2009) and the DER metric, which it summarizes; the NIST evaluation plans were not read.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 3 Performance Metrics",
  "method": "Challenge description: datasets from eleven domains, four tracks, two metrics computed with the dscore tool.",
  "limitations": "The arXiv version 1 was read, not the Interspeech proceedings version. The claim that most prior work used a modified DER is the authors' summary; the cited studies were not read.",
  "provenance": "PDF downloaded with curl from the URL above on 2026-11-18 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "Speaker diarization, often referred to as "who spoke when", is the task of determining how many speakers are present in a conversation and correctly identifying all segments for each speaker."
- Section 1: "the RT evaluations introduced the diarization error rate (DER) metric, which remains the principal evaluation metric in this area."
- Section 1: "the majority of this work has evaluated systems using a modified version of DER in which speech within 250 ms of reference boundaries and overlapped speech are excluded from scoring."
- Section 1: "As short segments such as backchannels and overlapping speech are both common in conversation, this may have resulted in an over-optimistic assessment of performance even within these domains"
- Section 1: "As with the NIST RT evaluations, DER is adopted as the primary evaluation metric, but without use of collars or exclusion of overlapping speech."
- Section 3: "For each system we also compute a secondary metric, Jaccard error rate (JER), which is newly developed for DIHARD II."
- Shows: the diarization metric moved from DER with a forgiveness collar and overlap exclusion back to full DER, plus a new per-speaker JER, and the stated reason is over-optimistic scores.
- Does not show: speaker identity. Diarization labels anonymous speakers; naming them is a separate step.
