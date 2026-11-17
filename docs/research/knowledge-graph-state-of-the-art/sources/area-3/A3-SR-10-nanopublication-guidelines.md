# A3-SR-10 — Nanopublication Guidelines (nanopub.net)

```json
{
  "source_identity": "Nanopublication Guidelines (working draft), https://nanopub.net/guidelines/working_draft/",
  "author_or_issuing_body": "Nanopublication community (authors not named on the page)",
  "publisher": "nanopub.net",
  "publication_date": "2026-11-17T00:00:00Z",
  "relevant_event_date": "2014-01-01",
  "source_family": "Primary. Community specification of the current nanopublication format. It cites A3-SR-06 (Groth 2010), A3-SR-07 (Kuhn 2013) and A3-SR-08 (Kuhn and Dumontier 2014) as foundations.",
  "precise_evidence_location": "Introduction; section 'Basic Elements' (assertion, provenance, publication info); section 'Integrity Key'; References.",
  "method": "A normative specification text with MUST and SHOULD rules and examples.",
  "limitations": "The page carries no publication date, no version number, no change log and no author list. The value in publication_date is the retrieval date, not a publication date. The event date is a lower bound: the reference list includes Kuhn and Dumontier 2014, so the text is not older than 2014. Quotes come from a model-assisted extraction and were not compared with the raw HTML. The page is a 'working draft', and the page text does not say whether a later version replaced it. It cannot show how the specification changed over time.",
  "provenance": "Fetched 2026-11-17 with the WebFetch tool from the URL above. Re-verify by opening the page and checking the 'Basic Elements' section."
}
```

## Evidence

- Introduction: nanopublications are "a community-driven approach to representing structured data along with its provenance as small self-contained and citable entities."
- 'Basic Elements': the assertion graph holds the statements that "form the main claim of the nanopublications". The provenance graph describes how the assertion came to be ("Provenance means 'how this came to be'") and "MUST contain a link to the assertion graph identifier". The publication info graph holds provenance about the nanopublication itself; its triples' subject "MUST be the nanopublication URI".
- 'Integrity Key': "Trusty URIs are the recommended way of assigning integrity keys to nanopublications."
- References: Groth et al. 2010, Mons et al. 2011, Kuhn et al. 2013, Carroll et al. 2005 (named graphs), Kuhn and Dumontier 2014.

## What the source shows

It shows the current three-graph structure of a nanopublication and the role of trusty URIs in it. The structure differs from the 2010 draft (A3-SR-06), which defined statements, annotations and S-Evidence.

## What the source does not show

It does not show why or when the structure changed, and it does not show an earlier specification version.

## Failed searches and gaps

An archived earlier version of the guidelines (the 2013 guidelines cited in the literature) was not located.
