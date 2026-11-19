# A1-SR-15: pgsql-hackers thread "new function for tsquery creartion" and the websearch_to_tsquery commit, 2017 to 2018

```json
{
  "source_identity": "Mailing list thread 'new function for tsquery creartion', pgsql-hackers, first message fe931111ff7e9ad79196486ada79e268@postgrespro.ru (https://www.postgresql.org/message-id/flat/fe931111ff7e9ad79196486ada79e268@postgrespro.ru); commit 1664ae1978bf0f5ee940dc2fc8313e6400a7e7da 'Add websearch_to_tsquery' (2018-04-05)",
  "author_or_issuing_body": "Victor Drobny and Dmitry Ivanov (patch authors, Postgres Professional); reviewers Thomas Munro, Alexey Chernyshov, Tomas Vondra, Aleksander Alekseev, Aleksandr Parfenov; Teodor Sigaev (committer)",
  "publisher": "PostgreSQL Global Development Group mailing list archive and git repository",
  "publication_date": "2018-04-05T16:55:11Z",
  "relevant_event_date": "2017-07-19",
  "source_family": "Primary: the project's mailing list archive and source repository. The 11 release note (A1-SR-14) summarises the result.",
  "precise_evidence_location": "Messages of Victor Drobny 2017-07-19 16:43:51; Teodor Sigaev 2018-03-22 14:38:04; Dmitry Ivanov 2018-03-26 08:51:42; Thomas Munro 2018-03-26 11:32:05; Dmitry Ivanov 2018-03-26 16:48:19; commit message of 1664ae1978",
  "method": "Patch proposal and review discussion; commit message.",
  "limitations": "The thread was read as a converted flat page; patch attachments were not read. Messages between November 2017 and January 2018 were skimmed. Quoted reviewer text is the reviewer's own words; quoted parts of earlier messages inside replies were left out.",
  "provenance": "Flat thread page downloaded with curl on 2026-11-18 and converted to text; commit read with gh api on 2026-11-18. Re-verify at the URL above."
}
```

## Evidence

- Drobny, 2017-07-19: "The main one is the to_tsquery function that allows to make query with any operation. But to make correct query all of the operators should be specified explicitly."
- Drobny, 2017-07-19: "In order to make it easier postgres has functions like plainto_tsquery and phraseto_tsquery which allow to make tsqueries from strings. But they are not flexible enough."
- Drobny proposes a function named queryto_tsquery with phrases in double quotes, a new operator AROUND(N), and aliases for `!` and `|`. Note: paraphrased, because the proposal text holds quotation marks.
- Sigaev, 2018-03-22: "I think new operator should be a subject for separate patch. And I prefer idea about range phrase operator."
- Ivanov, 2018-03-26: "The following version of patch won't support AROUND(N)."
- Munro, 2018-03-26: "Would it be OK to use user-supplied websearch strings? Ie can it produce a syntax error?"
- Ivanov, 2018-03-26: "After a private discussion with Theodor I came to a conclusion that the most beneficial outcome would be to suppress all syntax errors and give user some result, cutting all misused operators along the way."
- Commit 1664ae1 (2018-04-05): "Error-tolerant conversion function with web-like syntax for search query, it simplifies constraining search engine with close to habitual interface for users."
- What the source shows: the path from to_tsquery (strict syntax) and plainto_tsquery or phraseto_tsquery (no operators) to websearch_to_tsquery. Review removed the AROUND(N) operator and made the function reject no input.
- What the source does not show: whether the range phrase operator was ever committed; the current manual (A1-SR-06) lists only `<->` and `<N>`.
