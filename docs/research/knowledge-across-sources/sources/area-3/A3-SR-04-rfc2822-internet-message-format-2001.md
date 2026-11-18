# A3-SR-04: RFC 2822, Internet Message Format (2001)

```json
{
  "source_identity": "RFC 2822, 'Internet Message Format'; https://www.rfc-editor.org/rfc/rfc2822.txt",
  "author_or_issuing_body": "P. Resnick, Editor (QUALCOMM Incorporated)",
  "publisher": "RFC Editor (IETF, Standards Track)",
  "publication_date": "2001-04-01T00:00:00Z",
  "relevant_event_date": "2001-04-01",
  "source_family": "Primary. Internet message format lineage: obsoletes RFC 822 (A3-SR-02); obsoleted by RFC 5322 (A3-SR-05).",
  "precise_evidence_location": "Section 3.6.4 Identification fields (pages 23 to 25); Appendix B, items 23 and 24 (page 49 to 50)",
  "method": "Standards text with ABNF grammar and prose rules.",
  "limitations": "Only month and year are known; the date is set to 1 April 2001. The appendix lists changes but not the reasons for them. The mailing-list record of the IETF DRUMS working group, where the reasons would be, was not searched.",
  "provenance": "Plain text downloaded with curl from the URL above on 2026-11-18 and read in full for the cited sections. Re-verify at the same URL; RFC text is immutable once published."
}
```

## Evidence

- Section 3.6.4: "Though optional, every message SHOULD have a "Message-ID:" field. Furthermore, reply messages SHOULD have "In-Reply-To:" and "References:" fields as appropriate, as described below."
- Section 3.6.4 grammar: "in-reply-to = "In-Reply-To:" 1\*msg-id CRLF" and "msg-id = [CFWS] "\<" id-left "@" id-right ">" [CFWS]". Phrases are no longer allowed in the generated form.
- Section 3.6.4: "In all cases, it is the meaning that the sender of the message wishes to convey (i.e., whether this is the same message or a different message) that determines whether or not the "Message-ID:" field changes, not any particular syntactic difference that appears (or does not appear) in the message."
- Section 3.6.4: "The "References:" field will contain the contents of the parent's "References:" field (if any) followed by the contents of the parent's "Message-ID:" field (if any)."
- Section 3.6.4 note: "These implementations assume that each new message is a reply to a single parent and hence that they can walk backwards through the "References:" field to find the parent of each message listed there. Therefore, trying to form a "References:" field for a reply that has multiple parents is discouraged and how to do so is not defined in this document."
- Section 3.6.4: "The message identifier (msg-id) itself MUST be a globally unique identifier for a message."
- Appendix B: "23. Tightened syntax of in-reply-to and references.*" and "24. CFWS within msg-id not allowed.*"
- Shows: the mail standard adopts the netnews construction rule for References (A3-SR-03), restricts In-Reply-To and References to message identifiers, and names threading software as the reason for the single-parent limit.
- Does not show: evidence that mail software followed the new rule. A3-SR-06 and A3-SR-07 report that it often did not.
