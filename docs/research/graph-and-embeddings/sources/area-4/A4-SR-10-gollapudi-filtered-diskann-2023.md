# A4-SR-10: Gollapudi et al., Filtered-DiskANN: Graph Algorithms for Approximate Nearest Neighbor Search with Filters

```json
{
  "source_identity": "Siddharth Gollapudi, Neel Karia, Varun Sivashankar, Ravishankar Krishnaswamy, Nikit Begwani, Swapnil Raz, Yiyong Lin, Yin Zhang, Neelam Mahapatro, Premkumar Srinivasan, Amit Singh, Harsha Vardhan Simhadri, 'Filtered-DiskANN: Graph Algorithms for Approximate Nearest Neighbor Search with Filters', Proceedings of the ACM Web Conference 2023 (WWW '23), doi:10.1145/3543507.3583552; https://harsha-simhadri.org/pubs/Filtered-DiskANN23.pdf",
  "author_or_issuing_body": "Gollapudi, Karia, Sivashankar, Krishnaswamy, Simhadri (Microsoft Research India) and co-authors at Microsoft India and Microsoft USA",
  "publisher": "ACM (WWW '23); PDF hosted on an author's homepage",
  "publication_date": "2023-04-30T00:00:00Z",
  "relevant_event_date": "2023-04-30",
  "source_family": "Primary for FilteredVamana and StitchedVamana. Secondary for its descriptions of post-processing, per-label indexes, and inline filtering in other systems. Same research group as DiskANN (A4-SR-05).",
  "precise_evidence_location": "Abstract; Section 2 (prior methods and their drawbacks)",
  "method": "Algorithm design plus experiments on real-world datasets with natural labels.",
  "limitations": "publication_date is the first day of the conference. The author-hosted PDF may differ from the ACM print. The paper limits itself to exact match with one filter label per query, as it states. Its descriptions of Weaviate, Milvus, and Pinecone are product facts for area 2 and are not used here.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at the URL above or by the DOI."
}
```

## Evidence

- Abstract: "There has been little prior work on algorithms that use label metadata associated with vector data to build efficient indices for filtered ANNS queries. Consequently, current indices have high search latency or low recall which is not practical in interactive web-scenarios."
- Section 2: "One straightforward method for answering hybrid queries is the post-processing approach: build a standard ANNS index, query as usual, and post-process the results by selecting only those results returned by the index that match the query filter. While this method is easy to implement, it performs poorly in practice."
- Section 2: "Conversely, one might consider a trivial pre-processing method that builds a separate index for each possible filterable label 𝑓 ∈ F so that a query can be routed to the index associated with the query’s filter. However, such an approach would quickly become prohibitively expensive in scenarios with either a large number of filters, or where each point could have many associated filters."
- Abstract: "Central to our algorithms is the construction of a graph-structured index which forms connections not only based on the geometry of the vector data, but also the associated label set."
- Shows: the criticism of post-filtering and of one index per label, and the response of a graph index whose edges depend on labels.
- Does not show: range predicates, multi-label conjunctions beyond its stated scope, or behaviour when the label set is large and unknown at build time.
