# A4-SR-04: Malkov, Yashunin, Efficient and Robust Approximate Nearest Neighbor Search Using Hierarchical Navigable Small World Graphs

```json
{
  "source_identity": "Yu. A. Malkov, D. A. Yashunin, 'Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs', arXiv:1603.09320 (latest version v4); later published in IEEE TPAMI 42(4), 2020; https://arxiv.org/pdf/1603.09320",
  "author_or_issuing_body": "Yu. A. Malkov, D. A. Yashunin",
  "publisher": "arXiv (Cornell University)",
  "publication_date": "2018-08-14T00:00:00Z",
  "relevant_event_date": "2016-03-30",
  "source_family": "Primary for HNSW. Secondary for the k-nearest-neighbour graph approaches and for navigable small world (NSW) by the same first author, which it summarises in Section 2.",
  "precise_evidence_location": "Abstract; Section 1 Introduction; Section 2.1 Proximity graph techniques; Section 4.2.3 Memory cost; Section 6 Conclusion",
  "method": "Algorithm design plus experiments against other open-source libraries on public vector datasets.",
  "limitations": "The arXiv listing shows v1 on 30 March 2016 and v4 on 14 August 2018; the downloaded PDF carries no version stamp, and publication_date assumes it is v4. The TPAMI print was not read. The NSW papers of 2012 to 2014 were not read, so the NSW statements come through this paper.",
  "provenance": "PDF Downloaded with curl on 2026-11-18 and extracted with pdftotext; quotes taken from the extracted text, with line-end hyphens rejoined. Re-verify at https://arxiv.org/abs/1603.09320."
}
```

## Evidence

- Section 2.1: "The main drawbacks of the k-NN graph approaches are: 1) the power law scaling of the number of steps with the dataset size during the routing process [28, 29]; 2) a possible loss of global connectivity which leads to poor search results on clusetered data."
- Section 2.1: "The NSW graph is constructed via consecutive insertion of elements in random order by bidirectionally connecting them to the M closest neighbors from the previously inserted elements."
- Section 2.1: "The NSW approach delivered the state-of-the-art performance on some datasets [33, 34], however, due to the overall polylogarithmic complexity scaling, the algorithm was still prone to"
- Note: the sentence above continues after a page header with the words severe performance degradation on low dimensional datasets, which the extracted text separates from the quote.
- Abstract: "Starting search from the upper layer together with utilizing the scale separation boosts the performance compared to NSW and allows a logarithmic complexity scaling."
- Section 4.2.3: "The memory consumption of the Hierarchical NSW is mostly defined by the storage of graph connections."
- Section 6: "add support for element updates and removal. One of the apparent shortcomings of the proposed ap"
- Note: the quote above breaks at a footnote in the extracted text. The sentence goes on to name the loss of distributed search compared to NSW.
- Shows: the sequence k-NN graph, then NSW, then HNSW, with the criticism the authors give for each earlier step, and the authors' own list of open points: updates, removal, and distributed search.
- Does not show: disk-resident indexes, filtered search, or measured behaviour after long streams of deletes.
