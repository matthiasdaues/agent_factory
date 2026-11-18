# A2-SR-04: Atanasova et al., Overview of the CLEF-2018 CheckThat! Lab, Task 1: Check-Worthiness

```json
{
  "source_identity": "Pepa Atanasova, Lluís Màrquez, Alberto Barrón-Cedeño, Tamer Elsayed, Reem Suwaileh, Wajdi Zaghouani, Spas Kyuchukov, Giovanni Da San Martino, Preslav Nakov, 'Overview of the CLEF-2018 CheckThat! Lab on Automatic Identification and Verification of Political Claims. Task 1: Check-Worthiness', CLEF 2018 working notes; arXiv:1808.05542",
  "author_or_issuing_body": "CheckThat! lab organisers (Qatar Computing Research Institute, Qatar University, HBKU and others)",
  "publisher": "CLEF 2018 (CEUR working notes); preprint on arXiv",
  "publication_date": "2018-08-08T00:00:00Z",
  "relevant_event_date": "2018-09-10",
  "source_family": "Primary: the CLEF CheckThat! task-definition lineage, first edition. Followed by A2-SR-08.",
  "precise_evidence_location": "Abstract; Section 1 Introduction (task definition, Figure 1 pipeline); Section 2 Related work (ClaimBuster comparison)",
  "method": "Shared-task overview. Labels come from the claims that one fact-checking organisation, FactCheck.org, chose to check in 2016 US presidential debates and speeches.",
  "limitations": "relevant_event_date 2018-09-10 stands for the CLEF 2018 conference and is approximate. The 2019 edition was not read; its definition is taken from the summary in A2-SR-08.",
  "provenance": "PDF downloaded with curl on 2026-11-18 and extracted with pdftotext (poppler). Words split by a hyphen at a line break are rejoined in the quotes; no other change. Re-verify at https://arxiv.org/abs/1808.05542."
}
```

## Evidence

- Section 1: "asking participants to build systems that can mimic the selection strategies of a particular fact-checking organization: factcheck.org. It is defined as follows: Given a transcription of a political debate/speech, predict which claims should be prioritized for fact-checking."
- Section 1: "The goal is to produce a ranked list of sentences ordered by their worthiness for fact-checking."
- Figure 1 caption: "First, the input document is analyzed to identify sentences containing check-worthy claims (this task), then these claims are extracted and normalized, and finally they are fact-checked."
- Section 2: "The ClaimBuster system did not try to mimic the check-worthiness decisions for any specific fact-checking organization" and "In contrast, our dataset is based on actual annotations by a fact-checking organization".
- Shows: check-worthiness reformulated as ranking that copies a fact-checker's selection, with ClaimBuster's general-public label as the stated contrast. Does not show: agreement between different fact-checkers on what to check.
