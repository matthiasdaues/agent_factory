# A1-SR-08: PostgreSQL 18 and 19 manual, text search dictionaries, with the Snowball sync note

```json
{
  "source_identity": "PostgreSQL 18 manual 12.6 Dictionaries (https://www.postgresql.org/docs/18/textsearch-dictionaries.html); PostgreSQL 19 manual 12.6 Dictionaries (https://www.postgresql.org/docs/19/textsearch-dictionaries.html); src/backend/snowball/README at commit 1eb1e8b5f366b78d5a0e3821c3a197b7ab0f6ea4 of REL_19_STABLE",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org and the git repository",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-12-15",
  "source_family": "Primary: the PostgreSQL manual and source tree. The stemming algorithms come from the Snowball project (A1-SR-09); the 19 stemmer update is also in the release notes (A1-SR-14).",
  "precise_evidence_location": "12.6 introduction and dictionary-list rule; 12.6.1 Stop Words; 12.6.3 Synonym Dictionary; 12.6.4 Thesaurus Dictionary, paragraph on reindexing; 12.6.5 Ispell Dictionary, paragraphs on compound words and the Hunspell note; 12.6.6 Snowball Dictionary (18 and 19 versions differ); snowball/README lines 31-33",
  "method": "Project manual stating dictionary templates and configuration; source README stating the upstream version.",
  "limitations": "Same page dating as A1-SR-01; relevant_event_date is the date of the Snowball commit that REL_19_STABLE syncs with. The 18 manual does not list the Snowball languages; the 19 manual does. Neither manual describes the german or english configuration mapping in detail; the built-in english_stem definition is shown and the german one is inferred to follow the same pattern. Whether the 18 branch syncs with the same Snowball commit was not checked.",
  "provenance": "Pages downloaded with curl on 2026-11-18 and diffed. README read from raw.githubusercontent.com on 2026-11-18. Re-verify at the URLs above."
}
```

## Evidence

- 12.6: "Dictionaries are used to eliminate words that should not be considered in a search (stop words), and to normalize words so that different derived forms of the same word will match."
- 12.6: "Normalization does not always have linguistic meaning and usually depends on application semantics."
- 12.6: "The general rule for configuring a list of dictionaries is to place first the most narrow, most specific dictionary, then the more general dictionaries, finishing with a very general dictionary, like a Snowball stemmer or simple, which recognizes everything."
- 12.6.1: "However, stop words do affect the positions in tsvector, which in turn affect ranking"
- 12.6.4: "Thesauruses are used during indexing so any change in the thesaurus dictionary's parameters requires reindexing. For most other dictionary types, small changes such as adding or removing stopwords does not force reindexing."
- 12.6.5: "The standard PostgreSQL distribution does not include any Ispell configuration files."
- 12.6.5: "Ispell dictionaries support splitting compound words; a useful feature."
- 12.6.5 example: `ts_lexize('norwegian_ispell', 'sjokoladefabrikk')` gives `{sjokoladefabrikk,sjokolade,fabrikk}`.
- 12.6.5 note: "MySpell does not support compound words. Hunspell has sophisticated support for compound words. At present, PostgreSQL implements only the basic compound word operations of Hunspell."
- 12.6.6 (18 and 19): "A Snowball dictionary requires a language parameter to identify which stemmer to use, and optionally can specify a stopword file name that gives a list of words to eliminate."
- 12.6.6 (19 only): "The available values of the language parameter are: arabic, armenian, basque, catalan, danish, dutch, dutch_porter, english, esperanto, estonian, finnish, french, german, greek, hindi, hungarian, indonesian, irish, italian, lithuanian, nepali, norwegian, polish, porter, portuguese, romanian, russian, serbian, spanish, swedish, tamil, turkish, and yiddish."
- 12.6.6 (19 only): "The porter algorithm is an old stemmer for English, and the dutch_porter algorithm is an old stemmer for Dutch (it was called dutch in PostgreSQL releases before 19)."
- 12.6.6: "A Snowball dictionary recognizes everything, whether or not it is able to simplify the word, so it should be placed at the end of the dictionary list."
- snowball/README: "We are currently synced with the Snowball git commit 2d2e312df56f2ede014a4ffb3e91e6dea43c24be of 2025-12-15."
- What the source shows: German and English stemming ship with PostgreSQL as Snowball dictionaries. Compound splitting is available only through an Ispell or Hunspell dictionary whose files the operator must supply and place on the server's disk.
- What the source does not show: the quality of German compound splitting with any particular Hunspell file, or whether the german Snowball stemmer splits compounds (A1-SR-09 says it does not).
