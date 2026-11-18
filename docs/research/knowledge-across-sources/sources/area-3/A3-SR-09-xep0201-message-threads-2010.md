# A3-SR-09: XEP-0201, Best Practices for Message Threads (2006 to 2010)

```json
{
  "source_identity": "XEP-0201, 'Best Practices for Message Threads', version 1.0 (2010-11-29); https://xmpp.org/extensions/xep-0201.html",
  "author_or_issuing_body": "Peter Saint-Andre, Ian Paterson, Kevin Smith",
  "publisher": "XMPP Standards Foundation",
  "publication_date": "2010-11-29T00:00:00Z",
  "relevant_event_date": "2006-12-20",
  "source_family": "Primary. XMPP extension lineage; companion to RFC 6121 (A3-SR-08).",
  "precise_evidence_location": "Section 1 Introduction; Section 2 Motivation; Section 3.1 Table 1; Appendix H Revision History, versions 0.1 to 1.0",
  "method": "Informational best-practice document; the revision history records each change with a date.",
  "limitations": "The revision history gives one-line reasons only. The discussion on the standards@xmpp.org list was not searched. relevant_event_date is the first version.",
  "provenance": "HTML downloaded with curl on 2026-11-18 and tags stripped locally. Re-verify at the URL above; older versions are said to be in https://xmpp.org/extensions/attic/ (not checked)."
}
```

## Evidence

- Section 1: "best practices for generating and handling message threads have never been well specified (e.g., in RFC 3921 [2] or RFC 6121 [3])."
- Section 2: threads let clients "Restart a conversation from message history."
- Table 1: thread inclusion is RECOMMENDED for chat and groupchat and OPTIONAL for headline and normal messages.
- Revision 0.2 (2007-01-23): "Equalized treatment of different message types (chat and groupchat not preferred over normal); required the use of UUIDs; specified use of In-Reply-To header"
- Revision 0.5 (2008-02-06): "Defined parent attribute and provided recommendations regarding creation of new threads and child threads."
- Revision 0.6 (2010-05-21): "removed implementation note about In-Reply-To SHIM header"
- Revision 0.7 (2010-07-12): "Removed definition of ThreadID syntax, semantics, and uniqueness because the revisions to RFC 3921 covers those topics."
- Shows: the XMPP thread model went through dated revisions, including a borrowed mail In-Reply-To header that was later dropped, and its identity rules moved into the core RFC.
- Does not show: why the In-Reply-To SHIM header was removed. The revision entry gives no reason.
