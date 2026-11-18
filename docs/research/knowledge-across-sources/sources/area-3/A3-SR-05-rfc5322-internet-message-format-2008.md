# A3-SR-05: RFC 5322, Internet Message Format (2008)

```json
{
  "source_identity": "RFC 5322, 'Internet Message Format'; https://www.rfc-editor.org/rfc/rfc5322.txt",
  "author_or_issuing_body": "P. Resnick, Editor (Qualcomm Incorporated)",
  "publisher": "RFC Editor (IETF, Standards Track)",
  "publication_date": "2008-10-01T00:00:00Z",
  "relevant_event_date": "2008-10-01",
  "source_family": "Primary. Internet message format lineage: obsoletes RFC 2822 (A3-SR-04). Current at the time of retrieval.",
  "precise_evidence_location": "Section 1.1 Scope; Section 3.6.4 Identification Fields (page 25 onward); Section 4.5.4 obsolete identification fields; Appendix B, list of changes from RFC 2822, items 9 and 13",
  "method": "Standards text with ABNF grammar and prose rules; obsolete syntax kept in Section 4 for parsing only.",
  "limitations": "Only month and year are known; the date is set to 1 October 2008. Errata to RFC 5322 were not checked. Appendix B lists changes without reasons.",
  "provenance": "Plain text downloaded with curl from the URL above on 2026-11-18 and read in full for the cited sections. Re-verify at the same URL; RFC text is immutable once published."
}
```

## Evidence

- Section 3.6.4: "The message identifier (msg-id) syntax is a limited version of the addr-spec construct enclosed in the angle bracket characters, "\<" and ">". Unlike addr-spec, this syntax only permits the dot-atom-text form on the left-hand side of the "@" and does not have internal CFWS anywhere in the message identifier."
- Section 3.6.4 grammar: "id-left = dot-atom-text / obs-id-left" and "no-fold-literal = "[" \*dtext "]"".
- Section 3.6.4: "A message identifier pertains to exactly one version of a particular message; subsequent revisions to the message each receive new message identifiers." RFC 2822 said 'instantiation' here.
- Section 4.5.4: "obs-in-reply-to = "In-Reply-To" \*WSP ":" \*(phrase / msg-id) CRLF" and "For purposes of interpretation, the phrases in the "In-Reply-To:" and "References:" fields are ignored."
- Appendix B, changes from RFC 2822: "9. Removed quoted-pair from domain literals and message identifiers.\*" and "13. Removed no-fold-quote from msg-id. Clarified syntax limitations."
- Shows: the current rule removes the quoted form of the left-hand side, so one identifier has one written form. Readers must still parse the RFC 822 forms and ignore their phrases.
- Does not show: the reason for removing no-fold-quote. RFC 5256 (A3-SR-07), published four months earlier, documents the matching problem the quoted form causes. The link between the two is an inference, not a statement in either text.
