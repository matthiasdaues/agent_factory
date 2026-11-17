# A4-SR-14: Oudshoorn, Ortiz, Simkus: SHACL validation in the presence of ontologies

```json
{
  "source_identity": "Anouk Oudshoorn, Magdalena Ortiz, Mantas Simkus. 'SHACL validation in the presence of ontologies: Semantics and rewriting techniques'. Artificial Intelligence 352 (2026) 104483, DOI 10.1016/j.artint.2026.104483. Open access, CC BY 4.0.",
  "author_or_issuing_body": "Anouk Oudshoorn, Magdalena Ortiz, Mantas Simkus (TU Wien)",
  "publisher": "Elsevier, Artificial Intelligence",
  "publication_date": "2026-01-13T00:00:00Z",
  "relevant_event_date": "2026-01-13",
  "source_family": "Primary. Peer-reviewed journal article. It builds on the authors' earlier core-model proposal (their reference 15) and on Motik-style minimal-model semantics (their references 6 and 14). Shares the authors Ortiz and Simkus with records 12 and 13.",
  "precise_evidence_location": "Abstract; Section 1 'Introduction' (pages 1-2), paragraphs on the open-world and closed-world gap and on minimal Skolem models",
  "method": "Obtained the PDF through the fetch tool on 2026-11-17, extracted its text with pdftotext, and read the abstract and the introduction.",
  "limitations": "The date is the 'available online' date printed on page 1. Its criticism of minimal-model semantics is the authors' own view. Only the abstract and introduction were read, so the core-model construction and the complexity results were not checked. The construction covers one fragment of OWL, a Horn description logic, only. The claim that validation under ontologies has no standard semantics rests on the paper's own statement.",
  "provenance": "PDF retrieved through the fetch tool on 2026-11-17, with text extracted locally. Re-verify with the DOI above and the abstract."
}
```

## Evidence

### The gap between OWL and SHACL

- Abstract: "OWL, designed for inferring facts from incomplete data, makes the open-world assumption, whereas SHACL is a constraint language that treats the data as complete and must be validated under the closed-world assumption. The combination of both formalisms is very appealing and has been called for, but their semantic gap is a major challenge."
- Section 1: the SHACL specification "calls for graph validation in the presence of OWL entailment [1, Section 1.5], but unfortunately, does not provide guidance on how to realise this."

### Criticism of minimal-model semantics

- Section 1: "One of these options, using minimal models of the Skolemnisation of the DL ontology, has been advocated for in the case of integrity constraints [6,14]. But even such models give very weak semantics in formalisms with negation such as SHACL."
- Section 1, example: a data graph that already satisfies all ontology axioms gets a negative validation result, because "the minimal model under the Skolem semantics adds a fresh node as a hasPet-child of john, without the label Hamster."

### The formulation

- Abstract: "we advocate a semantics for SHACL validation in the presence of ontologies based on core universal models," with a rewriting technique "that reduces SHACL validation in the presence of ontologies to standard validation."

### What this record supports

- It records the most recent step in concept 1: the open-world and closed-world combination is still an open research problem in 2026 (area index, concept 1, step 5).
