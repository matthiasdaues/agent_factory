# A3-SR-03: RFC 1036, Standard for Interchange of USENET Messages (1987)

```json
{
  "source_identity": "RFC 1036, 'Standard for Interchange of USENET Messages'; https://www.rfc-editor.org/rfc/rfc1036.txt",
  "author_or_issuing_body": "M. Horton (AT&T Bell Laboratories), R. Adams (Center for Seismic Studies)",
  "publisher": "RFC Editor",
  "publication_date": "1987-12-01T00:00:00Z",
  "relevant_event_date": "1987-12-01",
  "source_family": "Primary. Netnews lineage (obsoletes RFC 850), parallel to the mail lineage of A3-SR-02. Later replaced by RFC 5536, which was not read.",
  "precise_evidence_location": "Section 2.1.5 Message-ID (pages 5 to 6); Section 2.2.5 References",
  "method": "Standards text describing the header rules of Usenet news articles.",
  "limitations": "Only month and year are known; the date is set to 1 December 1987. RFC 5536 (2009), the later netnews format, was not read. The text does not show how often news software followed the rule.",
  "provenance": "Plain text downloaded with curl from the URL above on 2026-11-18 and read in full for the cited sections. Re-verify at the same URL; RFC text is immutable once published."
}
```

## Evidence

- Section 2.1.5: "The Message-ID may not be reused during the lifetime of any previous message with the same Message-ID. (It is recommended that no Message-ID be reused for at least two years.)"
- Section 2.1.5: "Programmers are urged not to make assumptions about the content of Message-ID fields from other hosts, but to treat them as unknown character strings."
- Section 2.2.5: "If the original message does have a "References" line, the follow-up message should have a "References" line containing the text of the original "References" line, a blank, and the Message-ID of the original message."
- Section 2.2.5: "The purpose of the "References" header is to allow messages to be grouped into conversations by the user interface program."
- Section 2.2.5: "It is permissible to not include the entire previous "References" line if it is too long."
- Shows: the first rule in the lineage that makes References an ordered ancestor list, built from the parent's References plus the parent's Message-ID, and that states its purpose as grouping messages into conversations.
- Does not show: how a reader should handle a truncated References line. The text permits truncation but leaves the method open.
