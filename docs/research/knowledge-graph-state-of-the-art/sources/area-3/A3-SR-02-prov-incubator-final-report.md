# A3-SR-02 — Provenance XG Final Report (W3C Incubator Group, 2010)

```json
{
  "source_identity": "Provenance XG Final Report, W3C Incubator Group Report, 8 December 2010, https://www.w3.org/2005/Incubator/prov/XGR-prov-20101214/",
  "author_or_issuing_body": "W3C Provenance Incubator Group. Editors: Yolanda Gil, James Cheney, Paul Groth, Olaf Hartig, Simon Miles, Luc Moreau, Paulo Pinheiro da Silva",
  "publisher": "World Wide Web Consortium (W3C)",
  "publication_date": "2010-12-08T00:00:00Z",
  "relevant_event_date": "2010-12-08",
  "source_family": "Primary. Incubator group report, the document from which the W3C Provenance Working Group took its mandate. Moreau, Groth and Gil also wrote the OPM specification (A3-SR-01), so the two are not independent.",
  "precise_evidence_location": "Abstract; Sections 5.2, 5.4.1, 5.5, 6.2, 7.1 and 7.2.",
  "method": "The group surveyed provenance models and use cases, mapped other vocabularies to the Open Provenance Model, and derived requirements and recommendations.",
  "limitations": "The page text is 118,118 characters; the extraction read the first 100,000 and not the last 18,118, which hold Section 8 and later parts. The report date is 8 December 2010 while the version URL carries 14 December 2010; the page date is used. Quotes come from a model-assisted extraction of the page, so they were not compared character by character with the raw HTML. The report is a survey by a group whose editors designed OPM, so its choice of OPM as reference model is not an independent judgment.",
  "provenance": "Fetched 2026-11-17 with the WebFetch tool from the URL above, two prompts, first 100,000 characters. Re-verify by opening the URL and checking Sections 5.2, 6.2 and 7.1."
}
```

## Evidence

Quotes are exact as returned by the extraction. Words outside quotation marks are close paraphrase.

- Abstract: "This document summarizes the findings of the group."
- Section 5.2: the group chose the Open Provenance Model as the reference model because it is "general and broad enough". It mapped the Provenir Ontology, the Provenance Vocabulary for Linked Data, Proof Markup Language, Dublin Core, PREMIS, the WOT schema, SWAN, the Semantic Web Publishing Vocabulary and the Changeset Vocabulary to it, with the mappings encoded in SKOS.
- Section 6.2: OPM "cannot be used to represent" provenance statements that hold independent of a Web resource's state, because OPM is oriented toward "immutable pieces of state".
- Section 5.4.1: general provenance models could express the needed information but are "not currently widely deployed". The report also notes "no common format and api" for accessing provenance across sites.
- Section 5.5: among the gaps, "No standard techniques for versioning and expressing provenance relationships linking versions of data."
- Section 7.1 lists eight broad recommendations. Two of them: "A provenance framework should allow referring to versions of objects as they evolve over time" and "A provenance framework should include a standard way to express the provenance of provenance assertions".
- Section 7.2: recommendations 1, 2 and 3 are the highest priorities.

## What the source shows

The report shows that in 2010 a W3C group picked OPM as the common reference, named what OPM could not represent (changing Web resources, versions), and set eight recommendations for a standard.

## What the source does not show

It does not show how the Working Group handled the recommendations. It gives no deployment figures. The last 18,118 characters are unread.

## Failed searches and gaps

None beyond the unread tail.
