# A2-SR-09: Foundations of an Alternative Approach to Reification in RDF (Hartig, Thompson)

```json
{
  "source_identity": "Hartig, Thompson: Foundations of an Alternative Approach to Reification in RDF. arXiv:1406.3399 (v1 13 June 2014; v3 16 December 2021), https://arxiv.org/abs/1406.3399",
  "author_or_issuing_body": "Olaf Hartig, Bryan Thompson",
  "publisher": "arXiv",
  "publication_date": "2014-06-13T00:00:00Z",
  "relevant_event_date": "2012-01-01",
  "source_family": "Primary. Original RDF* proposal; v3 adds an obsolescence note pointing to the RDF-star community group report (A2-SR-14).",
  "precise_evidence_location": "v3 front-page note; section 1 Introduction, Examples 1 and 2; section 2, Example 3; section 3.1",
  "method": "PDF downloaded through WebFetch and read with pdftotext. The text read is v3. The v1 date is used as publication date, but the obsolescence note dates from 2021.",
  "limitations": "The event date marks the Dagstuhl seminar 'Semantic Data Management' that the paper names as origin. The year 2012 is read from the citation key ACA+12 and is not verified; the day is a placeholder. The v1 text was not compared with v3 body text. The authors propose their own approach. Does not show adoption or the reasons for the later changes beyond the v3 note.",
  "provenance": "Retrieved on 2026-11-17 with WebFetch, WebSearch or curl; PDF read locally; re-verify at the arXiv URL and compare v1 with v3."
}
```

## Evidence

- Section 1: RDF reification has "two major shortcomings". First, four additional triples per reified triple are inefficient for exchange and management. Second, queries that reach metadata need extra subexpressions to match the four reification triples. Example 2 shows four extra triple patterns per reified triple.
- Section 1: the approach comes from discussion at a Dagstuhl seminar among Bryan Thompson, Orri Erling, Yrjana Rankka, and Olaf Hartig.
- Section 2: use a triple "directly in the subject position or object position of (other) triples", written \<<:bob foaf:age 23>>. The paper links this to the triple identifiers used inside Systap's Bigdata store.
- Abstract and section 2: the formalization is "backward compatible with standard RDF reification."
- v3 front note: the approach was renamed RDF-star and SPARQL-star. In the community group specification, quoted triples (formerly embedded triples) are no longer defined through standard reification, and a quoted triple is no longer implicitly asserted when it is a constituent of a nested triple. This is the record of what changed, not of why.
