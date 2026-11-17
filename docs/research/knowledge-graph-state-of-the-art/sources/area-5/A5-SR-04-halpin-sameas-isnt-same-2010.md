# A5-SR-04: Halpin et al., When owl:sameAs isn't the Same

```json
{
  "source_identity": "Harry Halpin, Patrick J. Hayes, James P. McCusker, Deborah L. McGuinness, Henry S. Thompson, 'When owl:sameAs isn't the Same: An Analysis of Identity in Linked Data', ISWC 2010, LNCS 6496, pp. 305-320; https://files.ifi.uzh.ch/ddis/iswc_archive/iswc/ab/2010/iswc2010.semanticweb.org/pdf/261.pdf",
  "author_or_issuing_body": "Halpin, Thompson (University of Edinburgh); Hayes (IHMC); McCusker, McGuinness (Rensselaer Polytechnic Institute)",
  "publisher": "Springer (LNCS 6496); author PDF hosted in the ISWC archive at the University of Zurich",
  "publication_date": "2010-01-01T00:00:00Z",
  "relevant_event_date": "2010-01-01",
  "source_family": "Primary. Extends the authors' earlier OWLED 2010, LDOW 2010 and RDF Next Steps papers (named in the acknowledgements; not read). Parallel to A5-SR-03.",
  "precise_evidence_location": "Abstract; Section 1; Section 4 (4.1 to 4.5); Section 5 (Similarity Ontology); Section 6 discussion of results; Section 7 Conclusion",
  "method": "Conceptual analysis of identity, a proposed ontology of similarity relations, and a rater experiment on randomly selected owl:sameAs statements from a Linked Data crawl, with kappa agreement statistics.",
  "limitations": "Only year of publication is known from the PDF; date set to 1 January 2010 and the month is not verified. The experiment has a small number of raters and shows wide standard deviations (for example 51% plus or minus 21%). Raters judged only from the RDF retrieved, so 27% of links could not be judged. It does not show how often the incorrect uses lead to wrong query answers; the authors name that as future work. It does not show that any alternative was adopted.",
  "provenance": "PDF downloaded with curl on 2026-11-17 and extracted with pdftotext. Re-verify at the URL above or at DOI 10.1007/978-3-642-17746-0_20."
}
```

## Evidence

- Abstract: "owl:sameAs can be viewed as encoding only one point on a scale of similarity, one that is often too strong for many of its current uses."
- Section 1: sameAs is defined as stating "that two URI references actually refer to the same thing" [OWL reference]. Example: dbpedia:Paris is asserted sameAs both cyc:CityOfParisFrance and cyc:Paris DepartmentFrance, while OpenCyc states these two are distinct.
- Section 1: "These intuitions almost always violate the rather strict logical semantics of identity demanded by owl:sameAs as officially defined."
- Section 4: varieties of identity and similarity, from referentially opaque identity to related. Section 5: the Similarity Ontology that systematises them.
- Section 6 results: "approximately 51% (+/- 21%) percent of the usage of sameAs seems correct"; a coarse-grained 'kind-of-similar-and-related-to' relation fits about 21% (+/- 3%); about 27% (+/- 19%) cannot be judged from the RDF retrieved.
- Section 7: "the Similarity Ontology explores too large of a design space to be reliably deployed. A simple similarity property would be quite useful to add to RDF, such as sub-property of rdfs:seeAlso." It also suggests relating identity to a worked-out semantics of named graphs.
- Section 7 closing sentence: "The (ab)use of sameAs in Linked Data is not a threat, it's an opportunity."
