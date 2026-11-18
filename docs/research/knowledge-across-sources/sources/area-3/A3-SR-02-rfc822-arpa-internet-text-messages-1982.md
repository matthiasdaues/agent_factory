# A3-SR-02: RFC 822, Standard for the Format of ARPA Internet Text Messages (1982)

```json
{
  "source_identity": "RFC 822, 'Standard for the Format of ARPA Internet Text Messages'; https://www.rfc-editor.org/rfc/rfc822.txt",
  "author_or_issuing_body": "David H. Crocker (University of Delaware)",
  "publisher": "RFC Editor",
  "publication_date": "1982-08-13T00:00:00Z",
  "relevant_event_date": "1982-08-13",
  "source_family": "Primary. Internet message format lineage: obsoletes RFC 733 (A3-SR-01); obsoleted by RFC 2822 (A3-SR-04).",
  "precise_evidence_location": "Section 4.1 syntax (msg-id rule and field list); Section 4.6.1 MESSAGE-ID, 4.6.2 IN-REPLY-TO, 4.6.3 REFERENCES (pages 23 to 24); Appendix C.3.5 and C.3.6",
  "method": "Standards text with an augmented BNF grammar and prose semantics.",
  "limitations": "The text gives the rule only. It does not record why the rule changed from RFC 733, apart from the short notes in Appendix C. Field usage in practice is documented elsewhere (A3-SR-06).",
  "provenance": "Plain text downloaded with curl from the URL above on 2026-11-18 and read in full for the cited sections. Re-verify at the same URL; RFC text is immutable once published."
}
```

## Evidence

- Section 4.1 syntax: "msg-id = "\<" addr-spec ">" ; Unique message id". The identifier now takes the form of an address inside angle brackets.
- Section 4.1 syntax: "/ "In-Reply-To" ":" \*(phrase / msg-id)" and "/ "References" ":" \*(phrase / msg-id)". Free phrases remain allowed.
- Section 4.6.1: "This field contains a unique identifier (the local-part address unit) which refers to THIS version of THIS message."
- Section 4.6.3: "The contents of this field identify other correspondence which this message references." The section adds that message identifiers, if used, must have the msg-id form.
- Appendix C.3.5: "The field-body is no longer a comma-separated list, although a sequence is still permitted."
- Shows: the 1982 rule keeps the RFC 733 meaning and changes the identifier syntax to the addr-spec form.
- Does not show: an order for References or a rule for building References from a parent message.
