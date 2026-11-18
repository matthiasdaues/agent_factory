# A3-SR-01: RFC 733, Standard for the Format of ARPA Network Text Messages (1977)

```json
{
  "source_identity": "RFC 733, 'Standard for the Format of ARPA Network Text Messages', NIC 41952; https://www.rfc-editor.org/rfc/rfc733.txt",
  "author_or_issuing_body": "David H. Crocker (Rand Corporation), John J. Vittal (Bolt Beranek and Newman), Kenneth T. Pogran (MIT), D. Austin Henderson Jr. (Bolt Beranek and Newman)",
  "publisher": "RFC Editor (ARPA Network Working Group)",
  "publication_date": "1977-11-21T00:00:00Z",
  "relevant_event_date": "1977-11-21",
  "source_family": "Primary. Internet message format lineage: RFC 733 (obsoletes RFC 561, 680, 724), obsoleted by RFC 822 (A3-SR-02).",
  "precise_evidence_location": "Section III syntax, field list (lines with 'Message-ID', 'In-Reply-To', 'References'); Section IV.B 'Reference Specification Fields', items 1 to 3 (page 23); Section V.D examples",
  "method": "Standards text. It defines header syntax in a BNF grammar and gives the meaning of each field in prose.",
  "limitations": "Only the day of publication is known from the title page. The text shows the rule; it does not show how mail software applied it in 1977. The working-group discussion that produced the fields was not searched.",
  "provenance": "Plain text downloaded with curl from the URL above on 2026-11-18 and read in full for the cited sections. Re-verify at the same URL; RFC text is immutable once published."
}
```

## Evidence

- Section III syntax: "/ "Message-ID" ":" mach-id ; Only one allowed" and "/ "In-Reply-To"":" #(phrase / mach-id)". So In-Reply-To and References accept free phrases as well as machine identifiers.
- Section IV.B.1: "This field contains a unique identifier (the phrase) which refers to THIS version of THIS message. The uniqueness of the message identifier is guaranteed by the host which generates it."
- Section IV.B.1: "A message identifier pertains to exactly one instantiation of a particular message; subsequent revisions to the message should each receive a new message identifier."
- Section IV.B.2: "The contents of this field identify previous correspondence which this message answers."
- Section V.D example: "Message-ID: \<4231.629.XYzi-What at Other-Host>". The host part uses the word 'at', not the '@' sign.
- Shows: the first formulation of the three identity fields that RFC 822 and its successors keep.
- Does not show: any rule for building a thread from these fields. References has no defined order.
