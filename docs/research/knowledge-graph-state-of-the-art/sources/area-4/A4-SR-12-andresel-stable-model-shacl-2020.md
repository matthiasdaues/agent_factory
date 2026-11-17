# A4-SR-12: Andresel et al.: Stable Model Semantics for Recursive SHACL

```json
{
  "source_identity": "Medina Andresel, Julien Corman, Magdalena Ortiz, Juan L. Reutter, Ognjen Savkovic, Mantas Simkus. 'Stable Model Semantics for Recursive SHACL'. WWW '20 (The Web Conference 2020), pp. 1570-1580, DOI 10.1145/3366423.3380229. Abstract read through the Semantic Scholar API record.",
  "author_or_issuing_body": "Medina Andresel, Julien Corman, Magdalena Ortiz, Juan L. Reutter, Ognjen Savkovic, Mantas Simkus",
  "publisher": "ACM (The Web Conference 2020); abstract text served by Semantic Scholar",
  "publication_date": "2020-04-19T00:00:00Z",
  "relevant_event_date": "2020-04-19",
  "source_family": "Primary for the abstract, which is the authors' own text. The page read is a metadata copy at Semantic Scholar, so this record covers the abstract only. A Wikidata record gives 2020-05-04 as the publication date. The two dates differ. The Semantic Scholar date is used here.",
  "precise_evidence_location": "Abstract as returned by the Semantic Scholar Graph API for DOI 10.1145/3366423.3380229",
  "method": "Queried the Semantic Scholar Graph API on 2026-11-17 for the abstract and date. The ACM page returned HTTP 403, so the full text was not read.",
  "limitations": "Abstract only. The full paper, its examples, and its proofs were not read. The paper's own account of the weaknesses of the supported model semantics is limited to the abstract. The later papers in records 13 and 14 describe the paper's contribution in their own words.",
  "provenance": "API response retrieved on 2026-11-17 from api.semanticscholar.org. Re-verify by opening DOI 10.1145/3366423.3380229 and comparing the abstract."
}
```

## Evidence

### Criticism of the earlier proposals

- Abstract: "The recommendation left open the semantics of recursive shapes, but proposals have emerged recently to extend the official semantics to support recursion. These proposals are based on the principle of possibility (or non-contradiction): a graph is considered valid against a schema if one can assign shapes to nodes in such a way that all constraints are satisfied."
- Abstract: "This semantics is not constructive, as it does not provide guidelines about how to obtain such an assignment, and it may lead to unfounded assignments, where the only reason to assign a shape to a node is that it allows validating the graph."

### The formulation

- Abstract: "a stricter, more constructive semantics for SHACL, based on stable models, which are well-known in Answer Set Programming (ASP)," which "additionally requires a shape assignment to be properly justified by the input constraints."
- Abstract: the semantics "enjoys computationally tractable validation in the presence of constraints with stratified negation (as opposed to the previous semantics)," and a 3-valued version is "tolerant to certain faults in the schema or data."

### What this record supports

- It records the stable model step in concept 3 and the criticism of the supported model semantics that drove it (area index, concept 3, step 7). The step for the supported model semantics itself rests on secondary sources, see Gaps.
