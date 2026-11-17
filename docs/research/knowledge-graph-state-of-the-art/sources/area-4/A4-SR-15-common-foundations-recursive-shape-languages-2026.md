# A4-SR-15: Ahmetaj et al.: Common Foundations for Recursive Shape Languages

```json
{
  "source_identity": "Shqiponja Ahmetaj, Iovka Boneva, Jan Hidders, Maxime Jakubowski, Jose-Emilio Labra-Gayo, Wim Martens, Fabio Mogavero, Filip Murlak, Cem Okulmus, Ognjen Savkovic, Mantas Simkus, Dominik Tomaszuk. 'Common Foundations for Recursive Shape Languages'. arXiv:2604.20946v2 [cs.LO]. https://arxiv.org/abs/2604.20946",
  "author_or_issuing_body": "The twelve authors above, from TU Wien, Lille, Birkbeck, Oviedo, Bayreuth, Napoli, Warsaw, Paderborn, Bolzano, Umea, and Bialystok",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2026-05-13T00:00:00Z",
  "relevant_event_date": "2026-05-13",
  "source_family": "Primary for its comparison and its test study. Secondary for its history of recursion in ShEx and SHACL. The authors include people behind the ShEx specification and behind the supported, stable, and well-founded SHACL semantics (records 10, 12, and 13).",
  "precise_evidence_location": "Abstract; Section 1 (Introduction and Related Work); Section 2.3 'Classic Recursive Semantics'; Section 3 (comparative study of implementations); Section 4.3 and the conclusion (complexity)",
  "method": "Fetched the HTML version on 2026-11-17, converted it to plain text, and matched the quotes against that text. The complexity statement is quoted with its macro names rendered as LFP, GFP, and SMS.",
  "limitations": "The date is that of version 2 stamped on the page, 13 May 2026. The first submission date was not found. A preprint without a stated venue. Its validator tests cover a small set: pySHACL, SHACL-S, Jena SHACL, Topbraid, rudof, ShEx-S, and Jena ShEx. The paper does not discuss the stable and well-founded semantics beyond naming them. Only the first 100,000 characters of the page were read.",
  "provenance": "Retrieved from https://arxiv.org/html/2604.20946 on 2026-11-17 with curl. Re-verify by searching the text for 'left the semantics of recursion undefined'."
}
```

## Evidence

### History as the authors tell it

- Section 1: "the W3C recommendation [33] notably left the semantics of recursion undefined. The challenges of recursion were first formally addressed by Corman et al., who proposed a supported model semantics."
- Section 2.3: "The downside of the supported model semantics is that it allows multiple conforming shape assignments, which can be counter-intuitive and computationally expensive."

### Comparison of semantics

- Summary of complexity results: "LFP and GFP allow polynomial-time data complexity for all languages, whereas SMS immediately leads to intractability, even for very simple languages." LFP is the least fixpoint, GFP the greatest fixpoint, and SMS the supported model semantics.
- Section 1: "tests reveal that current tools implicitly commit to different semantics, which leads to non-uniform behaviour across implementations. In a nutshell, ShEx validators seem to implement GFP, whereas SHACL validators are more heterogeneous."

### What this record supports

- It records that, in 2026, ShEx and SHACL validators disagree on recursion, and that the authors of a common-foundations paper compare three semantics for it (area index, concept 3, step 9).
