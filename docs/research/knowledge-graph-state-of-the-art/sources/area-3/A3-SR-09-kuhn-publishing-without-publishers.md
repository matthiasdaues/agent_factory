# A3-SR-09 — Kuhn et al., "Publishing without Publishers" (arXiv preprint of the 2016 PeerJ paper)

```json
{
  "source_identity": "Kuhn, T., Chichester, C., Krauthammer, M., Dumontier, M., 'Publishing without Publishers: a Decentralized Approach to Dissemination, Retrieval, and Archiving of Data', arXiv:1411.2749v2; related published paper: Kuhn et al., 'Decentralized provenance-aware publishing with nanopublications', PeerJ Computer Science 2:e78, 2016",
  "author_or_issuing_body": "Tobias Kuhn, Christine Chichester, Michael Krauthammer, Michel Dumontier",
  "publisher": "arXiv",
  "publication_date": "2015-07-22T00:00:00Z",
  "relevant_event_date": "2014-11-01",
  "source_family": "Primary. Same research group as A3-SR-07 and A3-SR-08. The PeerJ 2016 paper has more authors and a different title; this record covers the arXiv preprint only.",
  "precise_evidence_location": "Abstract; Section 1 'Introduction', paragraphs 2 and 3 (list of problems with repositories) and the paragraph on trusty URIs.",
  "method": "A design paper with a prototype server network and an evaluation of the small network.",
  "limitations": "The date is that of arXiv version 2; version 1 dates from November 2014 (identifier 1411), and the first day of that month stands as the event date. The PeerJ paper could not be fetched (HTTP 403 and a bot check), so the published version is known only by its abstract on the author's page. The evaluation was not read. The authors argue for their own architecture and name the drawbacks of the alternatives they chose against.",
  "provenance": "Fetched 2026-11-17 with curl from https://arxiv.org/pdf/1411.2749 and converted with pdftotext. Quotes are exact and were checked against the extracted text. The PeerJ citation and abstract were read at https://ruben.verborgh.org/publications/kuhn_peerjcs_2016/."
}
```

## Evidence

- Abstract: "there exist currently no efficient, reliable, and agreed-upon methods for publishing scientific datasets". The authors propose "a server network to decentrally store and archive data in the form of nanopublications".
- Section 1, on existing repositories such as Figshare and Dryad: "they have nevertheless a number of drawbacks: They have centralized architectures, they give us no possibility to check whether the data have been (deliberately or accidentally) modified, and they do not support access or referencing on a more granular level than entire datasets (such as individual data entries)."
- Section 1: "Our approach is based on previous work, in which we proposed trusty URIs to make nanopublications and their entire reference trees verifiable and immutable by the use of cryptographic hash values [15,16]."
- Section 1: "A recent study found that more than half of the publicly accessible SPARQL endpoints are available less than 95% of the time [3]".

## What the source shows

It shows the next step after trusty URIs: a network of servers that store nanopublications and rely on the hash identifiers for verification, argued against centralized repositories.

## What the source does not show

It does not show that the network is used widely, and it does not show how the 2016 published version differs from this preprint.

## Failed searches and gaps

PeerJ article cs-78 was unreachable. A later account of the network is Kuhn et al. 2018 (arXiv:1809.06532), which the extraction tool summarized but which is not recorded here.
