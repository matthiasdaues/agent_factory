# A1-SR-18: W3C Web Annotation Data Model, Recommendation (2017)

```json
{
  "source_identity": "Web Annotation Data Model, W3C Recommendation 23 February 2017; https://www.w3.org/TR/2017/REC-annotation-model-20170223/ (latest version https://www.w3.org/TR/annotation-model/)",
  "author_or_issuing_body": "W3C Web Annotation Working Group; editors Robert Sanderson and others",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2017-02-23T00:00:00Z",
  "relevant_event_date": "2013-02-11",
  "source_family": "Primary. W3C Web Annotation lineage; builds on the Open Annotation Community Group drafts (A1-SR-17).",
  "precise_evidence_location": "Section 1 Introduction; section 3.1 Annotations; section 3.3.2 Agents (creator); section 3.3.1 Lifecycle Information (created); section 4.2 Selectors (Text Quote Selector, Text Position Selector); the States section (Time State); Appendix 'Changes from the Open Annotation Draft'",
  "method": "Standards specification, advanced to Recommendation after an implementation report with at least two independent implementations of each feature.",
  "limitations": "A data model only; it says nothing about how many systems use it. The editor list was read only up to 'Robert Sanderson'. relevant_event_date is the Open Annotation Community Draft 2 date from A1-SR-17.",
  "provenance": "HTML page of the latest version downloaded with curl on 2026-11-18; tags stripped with a local script; quotes checked against that text. The page identifies itself as the 23 February 2017 Recommendation. Re-verify at the URL above."
}
```

## Evidence

- Introduction: "Annotating, the act of creating associations between distinct pieces of information, is a pervasive activity online in many guises."
- Section 3.1: "An annotation is considered to be a set of connected resources, typically including a body and target, and conveys that the body is related to the target."
- Section 3.1: "There MUST be 1 or more target relationships associated with an Annotation."
- Section 3.3.2: "creator Relationship The agent responsible for creating the resource. This may be either a human, an organization or a software agent."
- Section 3.3.2: "creator of the Annotation is also useful for determining the trustworthiness of the Annotation."
- Section 3.3.1: "created Property The time at which the resource was created."
- Text Quote Selector: "The class for a Selector that describes a textual segment by means of quoting it, plus passages before or after it."
- Text Position Selector note: the selector "is very brittle with regards to changes to the resource. Any edits or dynamically transcluded content may change the selection, and thus it is RECOMMENDED that a State be additionally used to help identify the correct representation."
- Time State: "sourceDate Property The timestamp at which the Source resource SHOULD be interpreted for the Annotation."
- Changes appendix: "Introduce CSS Selector , XPath Selector and Range Selector from implementation experience."
- Changes appendix: "Add additional core lifecycle metadata for resources, including rights information and intended audience ."

What the source shows: the annotation is a resource of its own, stored apart from its target, with creator and creation time on the annotation. Selectors point into the target by quote or position, and a State records which version of the target was meant. This is a standard form of the external, annotated link that A1-SR-07 pointed to and that A1-SR-03 asked for.

What it does not show: any rule that the target learns about the annotation, so the reverse direction still needs a separate index. It does not record the evidence an annotation rests on beyond its body and target.
