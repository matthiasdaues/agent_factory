# A4-SR-06: W3C RDF Validation Workshop report

```json
{
  "source_identity": "RDF Validation Workshop: Practical Assurances for Quality RDF Data, Report, Cambridge MA, 10-11 September 2013. https://www.w3.org/2012/12/rdf-val/report",
  "author_or_issuing_body": "W3C workshop organizers; co-chairs Arnaud Le Hors and Harold Solbrig, assisted by Eric Prud'hommeaux. The page names no individual author of the report.",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2013-09-10T00:00:00Z",
  "relevant_event_date": "2013-09-10",
  "source_family": "Primary. Official W3C workshop report. It summarizes talks by the authors of Stardog constraints, ShEx, and OSLC Resource Shapes, so those later proposals (records 7 and 8) are not independent of this report.",
  "precise_evidence_location": "Executive Summary; 'Workshop Day 1' (ShEx talk after the meeting); 'Workshop Day 2' (Sirin and Ryman talks); 'Results'; 'Scope of Future Work'; 'Recommended Next Steps'",
  "method": "Fetched the page on 2026-11-17, converted it to plain text, and matched the quotes against that text.",
  "limitations": "The publication date is the first day of the workshop. The page prints no publication date for the report. It records the participants' summary, not a decision by the W3C. It says nothing about closed-world or open-world validation as a topic. It summarizes talks in a few lines each, so the arguments behind each position are not visible.",
  "provenance": "Retrieved from https://www.w3.org/2012/12/rdf-val/report on 2026-11-17 with curl. Re-verify by searching the page for 'does not constitute a complete solution'."
}
```

## Evidence

### Criticism of the existing options

- Executive Summary: "The participants agreed that there is currently no standard addressing these needs and the W3C should do something about it."
- Results: "while SPARQL plays a prominent role in how people tackle the validation problem today, participants agreed that SPARQL does not constitute a complete solution." The reason given: "SPARQL queries cannot easily be inspected and understood, either by human beings or by machines, to uncover the constraints that are to be respected."
- Workshop Day 2, on Evren Sirin: a Stardog solution "based on reusing the OWL syntax with a different semantics designed for validation rather than reasoning."
- Workshop Day 1, on Eric Prud'hommeaux: Shape Expressions, "an RDF grammar/validation language with a syntax similar to RelaxNG Compact Syntax." The same paragraph says "Some in the audience pushed back on the need for RDF validation at all."
- Workshop Day 2, on Arthur Ryman: OSLC Resource Shape, "an RDF vocabulary which provides a fairly limited but simple declarative solution."

### The call for a new formulation

- Scope of Future Work: the participants agreed on "a declarative way of describing simple integrity constraints along with an extension mechanism that allows using technologies such as SPARQL to specify more complex constraints."
- Recommended Next Steps: "IBM indicated that they intend to work on such a submission based on OSLC Resource Shape."
- Results: "The term 'shape' emerged as a popular label for these constraints."

### What this record supports

- It records the criticism that drove the change from SPARQL-based constraints (concept 2, step 1) to named shape languages (steps 3 and 4), and the first public step toward the W3C working group.
