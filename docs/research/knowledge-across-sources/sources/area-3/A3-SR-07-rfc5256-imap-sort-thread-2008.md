# A3-SR-07: RFC 5256, IMAP SORT and THREAD Extensions (2008)

```json
{
  "source_identity": "RFC 5256, 'Internet Message Access Protocol - SORT and THREAD Extensions'; https://www.rfc-editor.org/rfc/rfc5256.txt",
  "author_or_issuing_body": "M. Crispin (Panda Programming), K. Murchison (Carnegie Mellon University)",
  "publisher": "RFC Editor (IETF, Standards Track)",
  "publication_date": "2008-06-01T00:00:00Z",
  "relevant_event_date": "2008-06-01",
  "source_family": "Primary. IMAP extension lineage; its REFERENCES algorithm formalizes the algorithm of A3-SR-06. Refers to RFC 2822 (A3-SR-04) for msg-id.",
  "precise_evidence_location": "Section 1 historical note; Section 2.1 base subject; Section 3 THREAD command, ORDEREDSUBJECT and REFERENCES (pages 7 to 15); Section 6 Security Considerations",
  "method": "Standards text defining two server-side threading algorithms and the base-subject extraction rules.",
  "limitations": "Only month and year are known; the date is set to 1 June 2008. The draft history from 2002 to 2008 was not read, so the order in which the notes were added is unknown.",
  "provenance": "Plain text downloaded with curl from the URL above on 2026-11-18 and read in full for the cited sections. Re-verify at the same URL; RFC text is immutable once published."
}
```

## Evidence

- Section 1: "Historical note: The REFERENCES threading algorithm is based on the [THREADING] algorithm written and used in "Netscape Mail and News" versions 2.0 through 3.0."
- ORDEREDSUBJECT: "The ORDEREDSUBJECT threading algorithm is also referred to as "poor man's threading"." and "Hence, there are no grandchildren in ORDEREDSUBJECT threading."
- REFERENCES note: "The actual text in RFC 2822 may use quoting, resulting in multiple ways of expressing the same Message ID. Implementations of the REFERENCES threading algorithm MUST normalize any msg-id in order to avoid false non-matches due to differences in quoting."
- REFERENCES note: "Although [RFC2822] permits multiple Message IDs in the In-Reply-To header, in actual practice this discipline has not been followed. For example, In-Reply-To headers have been observed with message addresses after the Message ID, and there are no good heuristics for software to determine the difference."
- REFERENCES rule: if a message has no usable References, "then use the first (if any) valid Message ID found in the In-Reply-To header line as the only reference (parent) for this message."
- Section 6: "sorting by REFERENCES can lead to misleading threading trees. For example, a message with false References: header data will cause a thread to be incorporated into another thread."
- Shows: a standards-track threading algorithm with two documented criticisms of RFC 2822: quoted msg-id forms break matching, and multiple In-Reply-To identifiers are not used in practice.
- Does not show: data behind 'in actual practice'. No count or corpus is given.
