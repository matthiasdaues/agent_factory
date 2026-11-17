# A3-SR-08 — Kuhn and Dumontier, "Trusty URIs" (2014)

```json
{
  "source_identity": "Kuhn, T. and Dumontier, M., 'Trusty URIs: Verifiable, Immutable, and Permanent Digital Artifacts for Linked Data', ESWC 2014, LNCS 8465, 395-410, arXiv:1401.5775v3",
  "author_or_issuing_body": "Tobias Kuhn (ETH Zurich) and Michel Dumontier (Stanford)",
  "publisher": "arXiv (preprint read); Springer (published version, DOI 10.1007/978-3-319-07443-6_27)",
  "publication_date": "2014-05-28T00:00:00Z",
  "relevant_event_date": "2014-01-01",
  "source_family": "Primary. Same research group as A3-SR-07 and A3-SR-09. It extends the nanopublication lineage with hash-based identifiers.",
  "precise_evidence_location": "Abstract; Section 1 'Introduction', paragraphs 4 to 6 and the list of five requirements.",
  "method": "A design paper with reference implementations and a performance evaluation.",
  "limitations": "Date is the arXiv version 3 date (28 May 2014). The first arXiv version (January 2014, from the identifier 1401.5775) is not dated in the text; the first day of that month stands as the event date. The evaluation was not read. The paper presents nanopublications as the use case and so frames immutability as a problem of nanopublications; it does not cite an external critic. The Springer text was not read.",
  "provenance": "Fetched 2026-11-17 with curl via the WebFetch tool's saved copy of https://arxiv.org/pdf/1401.5775 and converted with pdftotext. Quotes are exact and were checked against the extracted text."
}
```

## Evidence

- Abstract: "we propose a technique to include cryptographic hash values in URIs. We call them trusty URIs and we show how they can be used for approaches like nanopublications to make not only specific resources but their entire reference trees verifiable."
- Section 1: "Published nanopublications are supposed to be immutable, but the current web has no mechanism to enforce this".
- Section 1: "nobody should be given the opportunity to silently modify his or her already published contributions."
- Section 1: nanopublications "consist not only of the actual scientific assertions but also of their provenance information and meta-data", so they carry their own identifying URI, and the hash must be computable even though the URI is part of the content.
- Section 1, requirement 3: "The verification should be performed on a more abstract level than just the bytes of a file, with modules for different types of content."
- Section 1, requirement 4: "The complete approach should be decentralized and open: Everybody should be allowed to make verifiable URIs without a central authority."

## What the source shows

It shows the problem (immutability promised, not enforced), the fix (hash in the URI, computed over the RDF content), and the five requirements the fix meets.

## What the source does not show

It does not show any security analysis from outside the authors, nor adoption outside the nanopublication network.

## Failed searches and gaps

The IEEE TKDE 2015 journal extension (Kuhn and Dumontier, "Making Digital Artifacts on the Web Verifiable and Reliable") was found by search but not read.
