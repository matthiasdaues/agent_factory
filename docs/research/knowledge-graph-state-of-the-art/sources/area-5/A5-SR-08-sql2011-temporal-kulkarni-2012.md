# A5-SR-08: Kulkarni and Michels, Temporal features in SQL:2011

```json
{
  "source_identity": "Krishna Kulkarni, Jan-Eike Michels, 'Temporal features in SQL:2011', SIGMOD Record 41(3), September 2012, pp. 34-43; https://sigmodrecord.org/publications/sigmodRecord/1209/pdfs/07.industry.kulkarni.pdf",
  "author_or_issuing_body": "Krishna Kulkarni, Jan-Eike Michels (IBM Corporation), members of the ISO SQL committee",
  "publisher": "ACM SIGMOD Record",
  "publication_date": "2012-09-01T00:00:00Z",
  "relevant_event_date": "2011-12-01",
  "source_family": "Secondary. Describes the ISO/IEC 9075:2011 standard text and the earlier TSQL2 proposals; the standard itself (paywalled) was not read. Authors worked on the standard.",
  "precise_evidence_location": "Section 1 Introduction; Section 2 (2.1 Periods, 2.4 Bitemporal tables, footnote 5); Section 3 Comparison with previous temporal proposals",
  "method": "Industry overview by committee members, with SQL examples.",
  "limitations": "Secondary description of the standard, not the standard. It is written by IBM authors who took part in the work, so it does not give an outside view. It covers relational tables, not graphs. It dates events by year only (1995, 2001, December 2011).",
  "provenance": "PDF downloaded with curl on 2026-11-17 and extracted with pdftotext. Re-verify at the URL above."
}
```

## Evidence

- Section 1: "In 1995, the ISO SQL committee initiated a project to create a new part of SQL standard devoted to the language extensions for the temporal data support. A set of language extensions based on (but not identical to) TSQL2 were submitted ... these proposals generated considerable controversy ... Eventually, the work on this new part was cancelled in 2001."
- Section 1: the new extensions were accepted into SQL:2011 Part 2 instead of a new part.
- Section 2: valid time is "the time period during which a row is" true in the real world; transaction time is the period during which the row is recorded in the database. SQL:2011 provides transaction time as a system-time period and valid time as an application-time period.
- Section 2.4: bitemporal tables combine both. "the system-time period automatically records when a particular name is known to the database, and the application-time period records when the name was legally effective."
- Footnote 5: "Though SQL:2011 does not define any specific term for such tables, we use the term 'bitemporal tables' in keeping with its use in the literature".
- Section 3: earlier proposals hid the period in an unnamed column to keep temporal upward compatibility. "One major drawback of this approach is that it is incompatible with SQL's notion of tables."
- Not shown: the 1985 origin of valid time and transaction time (Snodgrass and Ahn) and the TSQL2 text. Both are gaps.
