# A4-SR-10: Boneva, Labra Gayo, Prud'hommeaux, Staworko: Shape Expressions Schemas

```json
{
  "source_identity": "Iovka Boneva, Jose E. Labra Gayo, Eric G. Prud'hommeaux, Slawek Staworko. 'Shape Expressions Schemas'. arXiv:1510.05555v2 [cs.DB]. https://arxiv.org/abs/1510.05555",
  "author_or_issuing_body": "Iovka Boneva, Jose E. Labra Gayo, Eric G. Prud'hommeaux, Slawek Staworko",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2015-11-16T00:00:00Z",
  "relevant_event_date": "2015-11-16",
  "source_family": "Primary. Preprint by the ShEx authors that gives ShEx a formal semantics. It shares authors with record 8.",
  "precise_evidence_location": "Section 3.3 (well-defined schemas and Definition 1); Section 3.4 (witness-based semantics); Section 4.2 (termination)",
  "method": "Fetched the HTML version on 2026-11-17 and converted it to plain text. Matched the Section 3.3 quote and Definition 1 against the text. The other statements below are the fetch summary and were not matched line by line.",
  "limitations": "The date is that of version 2 stamped on the page. The page names no venue. Only the first 100,000 characters were read, so the related-work section on SHACL was not reached. The paper restricts negation to avoid cycles. It does not give a semantics for recursion through negation.",
  "provenance": "Retrieved from https://arxiv.org/html/1510.05555v2 on 2026-11-17 with curl. Re-verify by searching the text for 'well-defined'."
}
```

## Evidence

### Recursion and negation

- Section 3.3: the restriction exists "to guarantee well-defined semantics for ShEx schemas in presence of recursion and negation." It "requires that shape labels that appear negated do not lead to cyclic dependencies between shapes."
- Definition 1 (well-defined schema): if a shape label T appears negated in the definition of S, the sub-graph accessible from T in the dependency graph is acyclic (a directed acyclic graph).
- Section 3.4: validity of a graph "is a global property on the graph" and the global typing witness is defined recursively. Theorem 3.3 shows the definition is well-founded.

### What the paper does not do

- It does not define a semantics for shapes that refer to themselves through a negation. It rules them out.

### What this record supports

- It records the third formulation of recursion in concept 3: recursion allowed, negation through cycles forbidden (area index, concept 3, step 4). The step answers the open question in record 9, section 8, for ShEx.
