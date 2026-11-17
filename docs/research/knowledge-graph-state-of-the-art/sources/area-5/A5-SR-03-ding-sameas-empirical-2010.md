# A5-SR-03: Ding et al., owl:sameAs and Linked Data: An Empirical Study

```json
{
  "source_identity": "Li Ding, Joshua Shinavier, Tim Finin, Deborah L. McGuinness, 'owl:sameAs and Linked Data: An Empirical Study', Second Web Science Conference, Raleigh NC, 26-27 April 2010; https://publications.csee.umbc.edu/publications/473",
  "author_or_issuing_body": "Li Ding, Joshua Shinavier (Rensselaer Polytechnic Institute); Tim Finin (UMBC); Deborah L. McGuinness (Rensselaer Polytechnic Institute)",
  "publisher": "Web Science Conference 2010 proceedings; PDF hosted by UMBC eBiquity repository",
  "publication_date": "2010-04-26T00:00:00Z",
  "relevant_event_date": "2009-01-01",
  "source_family": "Primary. Linked Data empirical study by the Rensselaer group; parallel to Halpin et al. (A5-SR-04), which it cites as [4]. It also cites Vatant 2007 and Passant 2007 blog-level sources.",
  "precise_evidence_location": "Abstract; Section 2 (2.1 to 2.4, Known issues with owl:sameAs); Section 5 Conclusion",
  "method": "Pilot study on a small subset of Linked Data. It reviews issues reported by developers, defines metrics for owl:sameAs usage, and discusses strategies for consuming sameAs links.",
  "limitations": "Date of the underlying data crawl is not stated in the text read; relevant_event_date is set to 2009-01-01 as a placeholder for the 2009 Billion Triples Challenge dataset the paper mentions. Pilot scale only. It reports no error rates for sameAs links. The 'issues' in Section 2 are anecdotes and examples, not measured frequencies. The Vatant and Passant sources are known only through this paper.",
  "provenance": "PDF fetched with WebFetch from https://publications.csee.umbc.edu/publications/473/resources/477 on 2026-11-17 and extracted with pdftotext. Re-verify at the same URL."
}
```

## Evidence

- Abstract: users "should be careful when handling owl:sameAs: in that URIs linked by owl:sameAs may not be appropriate for simple aggregation, and that recursively exploring owl:sameAs may lead to considerable network overhead."
- Introduction: the 2009 Billion Triples Challenge dataset "further reveals some 6.5 million owl:sameAs statements."
- Section 2.4 (Simple aggregation may cause errors): the equivalence "is often context-dependent, and is accurate only in the context of one application". Example: two FOAF profiles of one person; merging them lets a reasoner infer a job title at a university where the person never held it. Second example: the cc:license property wrongly propagated from the New York Times dataset to DBpedia via sameAs inference. Third: two population figures for Warsaw from DBpedia and Geonames.
- Section 2.2: Vatant (2007) suggested that owl:sameAs is not symmetric and that both owners should assert it.
- Section 5: "some URIs can be integrated in exclusive manner, i.e. such that only one should be chosen, as opposed to truly indistinguishable resources whose descriptions should be merged."
- Not shown: any proposal to replace owl:sameAs. The paper recommends choosing an interpretation per use.
