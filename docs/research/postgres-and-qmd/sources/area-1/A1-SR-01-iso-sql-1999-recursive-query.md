# A1-SR-01: ISO/IEC 9075-2:1999, recursive query and the search or cycle clause

```json
{
  "source_identity": "ANSI/ISO/IEC International Standard 9075-2:1999, Database Language SQL, Part 2: Foundation (SQL/Foundation), September 1999; copy at https://web.cecs.pdx.edu/~len/sql1999.pdf",
  "author_or_issuing_body": "ISO/IEC JTC 1/SC 32 and ANSI (INCITS H2)",
  "publisher": "ISO/IEC and ANSI; PDF copy hosted on a Portland State University staff page",
  "publication_date": "1999-09-01T00:00:00Z",
  "relevant_event_date": "1999-09-01",
  "source_family": "Primary: the text of the SQL:1999 standard itself, Part 2. The root of the lineage that PostgreSQL follows in A1-SR-02 to A1-SR-05.",
  "precise_evidence_location": "Subclause 7.12 <query expression>, Format, <with clause>; Subclause 7.13 <search or cycle clause>, Function and Format; Annex on feature T131 'Recursive query', item 81",
  "method": "Normative standard text: grammar rules and conformance rules.",
  "limitations": "Only the month is known; the date is set to 1 September 1999 from the cover page. The PDF metadata gives a creation date of 23 September 1999. The copy sits on a university staff page, not on the ISO site, so it may differ from the sold edition; the cover says International Standard, not draft. Only subclauses 7.12, 7.13 and the T131 conformance rules were read. The document is 1,147 pages and was searched with pdftotext, not read in full.",
  "provenance": "Downloaded with curl from https://web.cecs.pdx.edu/~len/sql1999.pdf on 2026-11-18 and extracted with pdftotext -layout. pdfinfo: 1,147 pages, CreationDate 1999-09-23. Re-verify at that URL, or in the official ISO/IEC 9075-2:1999 edition."
}
```

## Evidence

- Subclause 7.12, Format: "<with clause> ::= WITH [ RECURSIVE ] <with list>"
- Subclause 7.13, Function: "Specify the generation of ordering and cycle detection information in the result of recursive query expressions."
- Subclause 7.13, Format: "SEARCH <recursive search order> SET <sequence column>"
- Subclause 7.13, Format, the cycle clause in full: "CYCLE <cycle column list> SET <cycle mark column> TO <cycle mark value> DEFAULT <non-cycle mark value> USING <path column>"
- Subclause 7.13, Format: "DEPTH FIRST BY <sort specification list>" and "BREADTH FIRST BY <sort specification list>"
- Annex, item 81: "Without Feature T131, ‘‘Recursive query’’, a <query expression> shall not specify RECURSIVE." The inner marks are the standard's own typographic quotes; the passage is quoted whole.
- Note: in the 1999 grammar the cycle mark value and the non-cycle mark value are mandatory. A1-SR-04 records that PostgreSQL later made them optional per a draft of a later standard.
- What the source shows: recursive queries and the SEARCH and CYCLE clauses both entered SQL in the 1999 edition, with recursion as the optional feature T131.
- What the source does not show: why the committee added these features, or any criticism of them. No committee paper was found.
