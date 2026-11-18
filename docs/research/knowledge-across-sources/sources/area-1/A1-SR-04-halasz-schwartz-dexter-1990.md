# A1-SR-04: Halasz and Schwartz, The Dexter Hypertext Reference Model (1990)

```json
{
  "source_identity": "Frank G. Halasz and Mayer Schwartz, 'The Dexter Hypertext Reference Model', presented at the NIST Hypertext Standardization Workshop, Gaithersburg, MD, 16-18 January 1990; text reposted at https://delibera.ethosfera.org/hm/z6MkrvYZzMYaCxyjbFWsZicdPCrcVmiXvgeY3i65GERQjjoH/records/the-dexter-hypertext-reference-model",
  "author_or_issuing_body": "Frank G. Halasz (Xerox PARC); Mayer Schwartz (Tektronix Labs)",
  "publisher": "NIST Hypertext Standardization Workshop (original); reposted by a user on delibera.ethosfera.org, 6 July 2025",
  "publication_date": "1990-01-16T00:00:00Z",
  "relevant_event_date": "1988-10-01",
  "source_family": "Primary for the 1990 workshop text, as far as the repost reaches. The 1994 Communications of the ACM version and the Müller-Prove summary (A1-SR-05) are separate copies or derivatives of the same family.",
  "precise_evidence_location": "Abstract; Introduction; the paragraph on the origin of the name; the storage-layer paragraph on specifiers and anchors",
  "method": "Reference model. The authors abstract the common features of existing hypertext systems, agreed at two workshops, and formalise them in the Z specification language.",
  "limitations": "The repost ends after the anchor definition, so this record did not read the link and specifier definitions in the source itself; A1-SR-05 covers them as a secondary source. The repost is by a third party and may differ from the NIST proceedings. relevant_event_date 1988-10-01 is the month of the first Dexter Inn workshop, month only. The 1994 CACM version was not read.",
  "provenance": "HTML page downloaded with curl on 2026-11-18; tags stripped with a local script; quotes checked against that text. Re-verify against the NIST workshop proceedings or the 1994 CACM version, doi:10.1145/175235.175237."
}
```

## Evidence

- Abstract: "The Dexter model is an attempt to capture, both formally and informally, the important abstractions found in a wide range of existing and future hypertext systems."
- Abstract: "The goal of the model is to provide a principled basis for comparing systems as well as for developing interchange and interoperability standards."
- Abstract: "The storage layer describes the network of nodes and links that is the essence of hypertext."
- Introduction: the paper compares "NoteCards [Hala88], Neptune [Deli86a], KMS [Aksc88a], Intermedia [Yank88a] and Augment [Enge84a]".
- Introduction: "Yet these systems differ markedly in the specific data models and sets of functionality that they provide to their users."
- Origin of the name: "The first workshop was held in October, 1988 at the Dexter Inn in New Hampshire. Hence the name of the model."
- Storage layer: "In the Dexter model, this is accomplished by an indirect addressing entity called an anchor. An anchor has two parts: an anchor id and an anchor value."
- Storage layer: "Anchors can therefore be uniquely identified across the whole universe by a component UID, anchor id pair."

What the source shows: Dexter separates links from component content and addresses link ends through anchors, which keep a stable ID while the anchor value may change.

What it does not show, in the part read: the link definition, the direction values, and any provenance attributes on links.
