# A3-SR-08: RFC 6121, XMPP Instant Messaging and Presence, thread element (2011)

```json
{
  "source_identity": "RFC 6121, 'Extensible Messaging and Presence Protocol (XMPP): Instant Messaging and Presence'; https://www.rfc-editor.org/rfc/rfc6121.txt",
  "author_or_issuing_body": "P. Saint-Andre (Cisco)",
  "publisher": "RFC Editor (IETF, Standards Track)",
  "publication_date": "2011-03-01T00:00:00Z",
  "relevant_event_date": "2011-03-01",
  "source_family": "Primary. XMPP lineage: obsoletes RFC 3921 (not read). XEP-0201 (A3-SR-09) moved its ThreadID rules into this RFC.",
  "precise_evidence_location": "Section 5.2.5 Thread Element (pages 75 to 76)",
  "method": "Standards text with prose rules and XML examples.",
  "limitations": "Only month and year are known; the date is set to 1 March 2011. RFC 3921 (2004), the earlier text, was not read, so the 2004 rule is a gap.",
  "provenance": "Plain text downloaded with curl from the URL above on 2026-11-18 and read in full for the cited sections. Re-verify at the same URL; RFC text is immutable once published."
}
```

## Evidence

- Section 5.2.5: "The <thread/> element is not used to identify individual messages, only conversations or messaging sessions."
- Section 5.2.5: "The <thread/> element MAY possess a 'parent' attribute that identifies another thread of which the current thread is an offshoot or child."
- Implementation note: "The ability to specify both a parent thread and a child thread introduces the possibility of conflicts between thread identifiers for overlapping threads." and "It is up to the implementation how it will treat conflicts between such overlapping thread identifiers"
- Section 5.2.5: "The value of the <thread/> element is not human-readable and MUST be treated as opaque by entities; no semantic meaning can be derived from it, and only exact comparisons can be made against it."
- Shows: XMPP separates the conversation identifier (thread) from the message identifier, and allows one level of thread parentage per element.
- Does not show: a stable message identifier. The stanza 'id' attribute is not defined here as unique or durable; A3-SR-10 fills that role.
