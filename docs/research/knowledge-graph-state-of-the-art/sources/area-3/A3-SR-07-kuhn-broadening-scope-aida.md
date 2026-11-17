# A3-SR-07 — Kuhn et al., "Broadening the Scope of Nanopublications" (2013)

```json
{
  "source_identity": "Kuhn, T., Barbano, P. E., Nagy, M. L., Krauthammer, M., 'Broadening the Scope of Nanopublications', ESWC 2013, LNCS 7882, 487-501, arXiv:1303.2446v1",
  "author_or_issuing_body": "Tobias Kuhn, Paolo Emilio Barbano, Mate Levente Nagy, Michael Krauthammer (Yale University, ETH Zurich)",
  "publisher": "arXiv (preprint read); Springer (published version, DOI 10.1007/978-3-642-38288-8_33)",
  "publication_date": "2013-03-11T00:00:00Z",
  "relevant_event_date": "2013-03-11",
  "source_family": "Primary. Research paper by the group that later wrote the nanopublication tooling (A3-SR-08, A3-SR-09). The authors criticize and extend the Concept Web Alliance formulation (A3-SR-06).",
  "precise_evidence_location": "Abstract; Section 1 'Introduction', paragraph 'The novelty of nanopublications lies in the combination of four ideas'.",
  "method": "The paper proposes an extension, then reports a user study of AIDA sentence writing and an automatic extraction test. The study sizes were not read.",
  "limitations": "The preprint, not the Springer text, was read; differences are unknown. The authors' evaluation claims ('quickly and at high quality') are self-reported in the abstract and were not checked against the study section. The paper argues for its own extension, so it states the criticism of the earlier design in the form that suits its proposal. It does not show whether the community adopted AIDA.",
  "provenance": "Fetched 2026-11-17 with curl from https://arxiv.org/pdf/1303.2446 and converted with pdftotext. Quotes are exact and were checked against the extracted text. Re-verify with the same URL."
}
```

## Evidence

- Abstract: the paper extends "the existing concept of nanopublications — tiny entities of scientific results in RDF representation — to broaden their application range". The extension "uses English sentences to represent informal and underspecified scientific claims" in a scheme called AIDA (Atomic, Independent, Declarative, Absolute).
- Section 1: "The novelty of nanopublications lies in the combination of four ideas: (1) to subdivide scientific results into minimal pieces, (2) to represent these results — called assertions — in an RDF-based formal notation, (3) to attach RDF-based provenance information on this "atomic" level, and (4) to treat each of these tiny entities as a separate publication."
- Section 1, the criticism: "Number (2) strikes us as problematic: Requiring formal representations for scientific results seems to be unrealistic in many cases and might restrict the range of practical application considerably."
- Section 1, the change: "we propose to allow authors to attach English sentences to nanopublications, thus allowing for informal representations of scientific claims."
- Abstract: the interface "also exemplifies the use of nanopublications for non-scientific content, including meta-nanopublications that describe other nanopublications."

## What the source shows

It shows a named criticism of one design element (the requirement for a formal assertion) and the change that followed (informal AIDA sentences).

## What the source does not show

It does not show a reason beyond the authors' judgment that formal assertions are "unrealistic in many cases". It gives no adoption data.

## Failed searches and gaps

The user-study figures were not extracted.
