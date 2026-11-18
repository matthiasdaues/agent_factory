# A4-SR-15: Zhang, Ives, Roth, "Who said it, and Why?" Provenance for Natural Language Claims

```json
{
  "source_identity": "Yi Zhang, Zachary G. Ives, Dan Roth, '“Who said it, and Why?” Provenance for Natural Language Claims', Proceedings of ACL 2020, pp. 4416-4426, doi:10.18653/v1/2020.acl-main.406; https://aclanthology.org/2020.acl-main.406.pdf",
  "author_or_issuing_body": "Zhang, Ives, Roth (Department of Computer and Information Science, University of Pennsylvania)",
  "publisher": "Association for Computational Linguistics (ACL Anthology)",
  "publication_date": "2020-07-01T00:00:00Z",
  "relevant_event_date": "2020-07-01",
  "source_family": "Primary for the claim provenance graph, its edge labels, and its use in claim verification. Uses Snopes fact-check articles as its running example.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2.1 Definition 1 (Claim Provenance Graph) and Edge Label Set; footnote 2 (p. 4418); Section 4 Application: Claim Verification, prov-sources",
  "method": "Defines a labelled directed acyclic graph from earlier statements to a query claim. Extracts sources and statements from retrieved articles and labels edges with a textual entailment model. Uses source nodes with no incoming edge as independent voters for claim verification.",
  "limitations": "Month-only date; set to 1 July 2020 (ACL 2020 month). The authors state that the problem is not solved. Influence by an uncited source is out of scope. The follow-up paper (Zhang, Ives, Roth, ACL 2021, Politi-Prov) was not read.",
  "provenance": "PDF downloaded with curl on 2026-11-18 from the ACL Anthology and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "At the heart of these insights is the need to determine the provenance of claims — who first made a given claim, and how an original claim developed and changed over time (and potentially across contributors)."
- Section 2.1: "the presence of an edge (vi, vj) indicates that tsi(q) influences the creation of tsj(q) via relation l ∈ L."
- Section 2.1, Edge Label Set: "(1) identical, when a source quotes a statement from another source; (2) paraphrased, when a source describes the same statement with different words; (3) textually entailed, when the previous statement can support" the current one; "(4) motivated, when the previous statement potentially influences the appearance of the current one." The text continues: "One is triggered, (...) the other one is contradicted, when the derived statement has an opposite opinion."
- Section 1: "It is important to note that we have not solved the claim provenance problem. We introduce it and explain its importance, provide an initial formulation and an implementation."
- Footnote 2: "We leave for future work a richer model that might also allow for a source to make a claim after being indirectly influenced by another uncited source."
- Section 4: "we call sources, a.k.a all nodes of the graph all-sources, and independent sources, a.k.a all source nodes of the graph, prov-sources."
- Shows: the closest match in this area to the four reuse classes. Its labels map to verbatim (identical), altered (paraphrased, entailed), and reframed in part (contradicted). Source nodes without incoming edges stand for independent origins.
- Does not show: a frame label, or a way to detect uncited influence, so undisclosed reuse would be counted as independent.
