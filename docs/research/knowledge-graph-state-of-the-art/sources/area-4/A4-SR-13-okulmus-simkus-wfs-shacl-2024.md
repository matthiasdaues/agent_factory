# A4-SR-13: Okulmus and Simkus: SHACL Validation under the Well-founded Semantics

```json
{
  "source_identity": "Cem Okulmus, Mantas Simkus. 'SHACL Validation under the Well-founded Semantics'. Proceedings of the 21st International Conference on Principles of Knowledge Representation and Reasoning (KR 2024), pp. 553 ff., DOI 10.24963/kr.2024/52. https://proceedings.kr.org/2024/52/kr2024-0052-okulmus-et-al.pdf",
  "author_or_issuing_body": "Cem Okulmus (Umea University) and Mantas Simkus (Umea University and TU Wien)",
  "publisher": "KR Inc., KR 2024 proceedings",
  "publication_date": "2024-11-01T00:00:00Z",
  "relevant_event_date": "2024-11-01",
  "source_family": "Primary for its own proposal. Secondary for its account of Corman et al. 2018 and Andresel et al. 2020. Shares the author Simkus with record 12.",
  "precise_evidence_location": "Abstract (page 553) and Section 1 'Introduction' (pages 553-554), the paragraphs on the supported model and stable model semantics",
  "method": "Downloaded the PDF on 2026-11-17, extracted its text with pdftotext, and read the abstract and the introduction.",
  "limitations": "The date 2024-11-01 is a placeholder for the month of the conference. The paper prints no day, and the conference month was not confirmed on a primary page. Only the introduction and the first examples were read. The paper's criticism of earlier semantics is a competing author's view. The authors of those semantics did not answer it in any source read here.",
  "provenance": "Downloaded from the KR proceedings URL above on 2026-11-17 with curl. Re-verify by reading the third paragraph of Section 1."
}
```

## Evidence

### What the paper says about the earlier semantics

- Abstract: "the standard defines the semantics of non-recursive constraints only, leaving the case of recursive constraints open. This led to recent efforts into finding a suitable, mathematically crisp semantics."
- Section 1: the case of recursion "was intentionally left unspecified: it is currently up to the developers of SHACL validators to come up with ad-hoc solutions."
- Section 1, on the supported model semantics of Corman et al.: it "has two weaknesses: (a) the problem of deciding graph validity is intractable, and (b) it allows for unfounded (self-supported) justifications of inferences."
- Section 1, on the stable model semantics of Andresel et al.: it "solves (b) but still has the problem (a): the intractability (specifically, NP-hardness) of validation."
- Section 1: the 2-valued supported and stable semantics "do not achieve the expected resilience to 'outside' problems" beyond the validation targets. Corman et al. added a 3-valued version, which "still suffers from unfounded justifications and intractability."

### The formulation

- Abstract: "recursive SHACL can be naturally equipped with a semantics inspired in the well-founded semantics for recursive logic programs with default negation. This semantics is not only intuitive, but it is also computationally tractable, unlike the main previous proposals."

### What this record supports

- It supplies the criticism that drove the change from the supported to the stable and then to the well-founded semantics (area index, concept 3, steps 6 to 8). It is the only source read here for the step of Corman et al. 2018.
