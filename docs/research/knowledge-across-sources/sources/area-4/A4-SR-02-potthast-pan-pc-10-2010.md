# A4-SR-02: Potthast et al., An Evaluation Framework for Plagiarism Detection

```json
{
  "source_identity": "Martin Potthast, Benno Stein, Alberto Barron-Cedeno, Paolo Rosso, 'An Evaluation Framework for Plagiarism Detection', COLING 2010 Posters, pp. 997-1005; https://aclanthology.org/C10-2115.pdf",
  "author_or_issuing_body": "Potthast, Stein (Bauhaus-Universitaet Weimar); Barron-Cedeno, Rosso (Universidad Politecnica de Valencia)",
  "publisher": "COLING 2010 Organizing Committee (ACL Anthology)",
  "publication_date": "2010-08-01T00:00:00Z",
  "relevant_event_date": "2010-01-01",
  "source_family": "Primary for the PAN-PC-10 corpus and its obfuscation strategies. Secondary for the METER corpus (A4-SR-01 lineage), which it compares against.",
  "precise_evidence_location": "Abstract; Section 1.2 Related Work; Section 3.1 Real, Simulated, and Artificial Plagiarism; Section 3.3 Creating Artificial Plagiarism, Table 4; Section 4 Corpus Validation, Figure 1",
  "method": "Builds a plagiarism corpus with 64,558 artificial cases made by automatic obfuscation and 4,000 simulated cases rewritten by Mechanical Turk workers. Compares the similarity of source and rewritten passages under n-gram vector space models with the Clough09 and METER corpora.",
  "limitations": "Month-only date; set to 1 August 2010 (COLING 2010 month). relevant_event_date is the year of corpus construction and is approximate. The domain is plagiarism in books, not news. Artificial obfuscation does not preserve meaning. The validation uses n-gram similarity only.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "the PAN-PC-10 corpus, which contains 64 558 artificial and 4 000 simulated plagiarism cases, the latter generated via Amazon's Mechanical Turk."
- Section 1.2, on METER: "Although the corpus can be used to evaluate plagiarism detection its design does not support this task. This is maybe the reason why it has not been used more often. Furthermore, it is an open question whether or not cases of news reuse differ from plagiarism cases where the plagiarists strive to remain undetected."
- Section 3.1: "Since verbatim copies can be detected easily, plagiarists often rewrite ssrc to obfuscate their illegitimate act."
- Section 3.1: "Generating artificial plagiarism cases is a non-trivial task if one requires semantic equivalence between a source passage ssrc and the passage splg that is obtained by an automatic obfuscation of ssrc. Such semantics-preserving algorithms are still in their infancy".
- Section 3.3 names three obfuscation strategies: "Random Text Operations", "Semantic Word Variation", and "POS-preserving Word Shuffling".
- Section 4: "We interpret these results as follows: (1) Different kinds of plagiarism and text reuse do not differ very much under n-gram models."
- Shows: a graded model of altered reuse (no obfuscation, artificial obfuscation, human paraphrase) and a benchmark for detecting it. It also records the criticism that METER was built for news reuse, not for plagiarism detection.
- Does not show: any measure of whether a rewrite keeps the meaning, or any class for reframing.
