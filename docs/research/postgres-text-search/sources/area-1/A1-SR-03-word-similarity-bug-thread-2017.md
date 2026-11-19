# A1-SR-03: pgsql-bugs thread "pg_trgm word_similarity inconsistencies or bug", 2017

```json
{
  "source_identity": "Mailing list thread 'pg_trgm word_similarity inconsistencies or bug', pgsql-bugs and pgsql-hackers, first message CY4PR17MB13207ED8310F847CF117EED0D85A0@CY4PR17MB1320.namprd17.prod.outlook.com; https://www.postgresql.org/message-id/flat/CY4PR17MB13207ED8310F847CF117EED0D85A0@CY4PR17MB1320.namprd17.prod.outlook.com",
  "author_or_issuing_body": "Cristiano Coelho (report); Arthur Zakirov and Alexander Korotkov (Postgres Professional, replies)",
  "publisher": "PostgreSQL Global Development Group mailing list archive, postgresql.org",
  "publication_date": "2017-10-27T18:48:08Z",
  "relevant_event_date": "2017-10-30",
  "source_family": "Primary: the project's mailing list archive. Commit be8a7a6866 (A1-SR-02) cites this thread as its discussion.",
  "precise_evidence_location": "Message of Cristiano Coelho, 2017-10-27 18:48:08; reply of Arthur Zakirov, 2017-10-28 08:22:29; reply of Alexander Korotkov, 2017-10-30 18:08:21",
  "method": "User bug report with a reproduction table, followed by developer analysis.",
  "limitations": "Only the first three messages were read in full; later messages in the flat thread were skimmed. The report concerns release 9.6.4. The thread proposes a setting; the committed fix (A1-SR-02) is a new function instead, and the message that settled that choice was not located.",
  "provenance": "Flat thread page downloaded with curl on 2026-11-18 and converted to text. Re-verify at the URL above."
}
```

## Evidence

- Coelho, 2017-10-27: "word_similarity doesn’t seem to do exactly what the docs say, since it will match trigrams from multiple words rather tan doing a word by word comparison."
- Coelho's table shows `word_similarity('sage', 'message s')` = 0.8 and `word_similarity('sage', 'message sag')` = 1, where the reporter expects 0.3 and 0.5.
- Zakirov, 2017-10-28: "It computes maximum similarity using closest trigrams not considering order of 'sage' trigrams."
- Korotkov, 2017-10-30: "Possible solution could be forcing this extent boundaries to be at word boundaries. However, it would become less convenient to search for *part* of word. And we already have users adopt this feature."
- Korotkov proposes a setting that switches word_similarity to word boundaries, and documentation of both behaviours. Note: this is a summary of his numbered list.
- What the source shows: the criticism that led from word_similarity (9.6) to strict_word_similarity (11): matches that span several words, and a disagreement with the documented meaning.
- What the source does not show: why the final patch added a separate function instead of the proposed setting.
