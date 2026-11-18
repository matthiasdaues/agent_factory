# A3-SR-02: Cer et al., SemEval-2017 Task 1: Semantic Textual Similarity (STS Benchmark)

```json
{
  "source_identity": "Daniel Cer, Mona Diab, Eneko Agirre, Inigo Lopez-Gazpio, Lucia Specia, 'SemEval-2017 Task 1: Semantic Textual Similarity Multilingual and Cross-lingual Focused Evaluation', arXiv:1708.00055v1; https://arxiv.org/pdf/1708.00055",
  "author_or_issuing_body": "Cer (Google Research); Diab (George Washington University); Agirre, Lopez-Gazpio (University of the Basque Country); Specia (University of Sheffield)",
  "publisher": "arXiv (Cornell University); the paper is the task report of SemEval-2017",
  "publication_date": "2017-07-31T00:00:00Z",
  "relevant_event_date": "2012-01-01",
  "source_family": "Primary for the 2017 shared task and the STS Benchmark. Secondary for the STS tasks of 2012 to 2016, which it summarises.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; the task overview with the annotation scale of Table 1; the analysis of common errors of well-ranking systems",
  "method": "Shared-task report: human annotators grade sentence pairs on a 0 to 5 scale; systems are ranked by Pearson correlation with the human scores; the authors analyse the errors of well-ranking systems.",
  "limitations": "relevant_event_date 2012-01-01 stands for the start of the STS task series and is approximate. The error analysis covers the 2017 participant systems, which predate SBERT and SimCSE. The paper does not measure how often each error type occurs. The workshop proceedings version was not compared with the arXiv text.",
  "provenance": "PDF downloaded from https://arxiv.org/pdf/1708.00055 with curl on 2026-11-18 and extracted with pdftotext. Quotes are copied from the extracted text; hyphens that the PDF inserted at line breaks are removed. Re-verify at the URL above."
}
```

## Evidence

- Abstract: "Semantic Textual Similarity (STS) measures the meaning similarity of sentences."
- Abstract: "the STS Benchmark is introduced as a new shared training and evaluation set carefully selected from the corpus of English STS shared task data (2012-2017)."
- Section 1: "Semantic Textual Similarity (STS) assesses the degree to which two sentences are semantically equivalent to each other."
- Task overview: "The ordinal scale in Table 1 guides human annotation, ranging from 0 for no meaning overlap to 5 for meaning equivalence."
- Task overview: "The resulting annotations reflect both pragmatic and world knowledge and are more interpretable and useful within downstream systems."
- Error analysis, paraphrase in my words because the passage holds many inner quotation marks: the authors list five common errors of well-ranking systems. These are word sense, attribute importance, compositional meaning (a man carrying a canoe with a dog against a dog carrying a man in a canoe), negation (pairs with and without goggles scored as nearly equivalent), and semantic blending.
- Error analysis: "For multilingual and cross-lingual pairs, these issues are magnified by translation errors for systems"
- Shows: the definition of STS as graded meaning similarity, and a list of errors that include negation and word order.
- Does not show: a direction of the relation. The scale grades symmetric similarity, not entailment.
