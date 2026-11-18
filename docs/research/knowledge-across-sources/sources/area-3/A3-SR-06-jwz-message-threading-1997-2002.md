# A3-SR-06: Jamie Zawinski, message threading (1997 to 2002)

```json
{
  "source_identity": "Jamie Zawinski, 'message threading', web page; https://www.jwz.org/doc/threading.html",
  "author_or_issuing_body": "Jamie Zawinski (former Netscape Mail and News developer)",
  "publisher": "jwz.org (personal site)",
  "publication_date": "2002-01-01T00:00:00Z",
  "relevant_event_date": "1997-01-01",
  "source_family": "Primary for the threading algorithm used in Netscape Mail and News 2.0 and 3.0 and for the author's 1997 header survey. Secondary for RFC 822, RFC 1036, and RFC 2822, which it summarizes.",
  "precise_evidence_location": "Introduction; section 'In-Reply-To:' with the survey of 22,950 messages; section 'References:'; section 'The Algorithm'; closing section on Netscape 4.0",
  "method": "Practitioner description of an algorithm, with a count of In-Reply-To forms in a mail archive that the author collected in 1997.",
  "limitations": "The page states copyright 1997 to 2002 and no exact date; publication_date is set to 1 January 2002 and relevant_event_date to 1 January 1997, both approximate. The survey sample is the author's own archive and he states it was skewed. The criticism of Netscape 4.0 is one developer's account. The 2002 imapext-thread Internet-Draft it mentions was not read.",
  "provenance": "HTML downloaded with curl on 2026-11-18 (a browser User-Agent was needed), tags stripped locally. Re-verify at the URL above; the page has no version history."
}
```

## Evidence

- Introduction: "This is the threading algorithm that was used in Netscape Mail and News 2.0 and 3.0, and in Grendel."
- Introduction: "This algorithm is also described in the 2002 imapext-thread Internet Draft, which in 2008 became RFC 5256"
- In-Reply-To section: "RFC 822 defined the In-Reply-To header as, basically, a free-text header." and "So you're not guaranteed to be able to parse anything useful out of In-Reply-To if it exists, and even if it contains something that looks like a Message-ID, it might not be (especially since Message-IDs and email addresses have identical syntax.)"
- Survey: "In a survey of 22,950 mail messages with In-Reply-To headers:" 18,396 had at least one bracketed text, 4,554 had none, 714 had one bracketed address and no message ID. The most common form, 31%, was "NAME's message of TIME <ID@HOST>".
- References section: "The References header was defined by RFC 822 in 1982. It was defined in, effectively, the same way as the In-Reply-To header was defined: which is to say, its definition was pretty useless."
- References section: "it is not uncommon for multiple messages in the same thread to have seemingly-contradictory References data, so threading code must make an effort to do the right thing in the face of conflicting data."
- Note on Eudora: "they put the parent Message-ID in the In-Reply-To header, but do not duplicate it in the References header"
- Netscape 4.0 section: "4.0 eliminated the \`\`dummy thread parent'' step, which is an absolute necessity to get threading right in the case where you don't have every message"
- Netscape 4.0 section: "Threading is the act of presenting parent/child relationships, whereas sorting is the act of ordering siblings."
- Shows: field-level evidence that RFC 822 headers were not reliably machine-readable, and an algorithm that tolerates missing and contradictory references.
- Does not show: an independent measurement. The survey has no stated method beyond 'grepped', and no other study of the same archive was found.
