# A1-SR-05: PostgreSQL 18 and 19 manual, unaccent, with its SQL install script

```json
{
  "source_identity": "PostgreSQL 18 manual F.48 unaccent (https://www.postgresql.org/docs/18/unaccent.html); PostgreSQL 19 manual F.50 unaccent (https://www.postgresql.org/docs/19/unaccent.html); contrib/unaccent/unaccent--1.1.sql at commit 1eb1e8b5f366b78d5a0e3821c3a197b7ab0f6ea4 of REL_19_STABLE",
  "author_or_issuing_body": "PostgreSQL Global Development Group",
  "publisher": "PostgreSQL Global Development Group, postgresql.org and the git repository",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2025-09-25",
  "source_family": "Primary: the PostgreSQL manual and source repository. Same lineage as A1-SR-01.",
  "precise_evidence_location": "F.48 introduction; F.48.1 Configuration; F.48.2 Usage; F.48.3 Functions; unaccent--1.1.sql, the two CREATE FUNCTION unaccent statements",
  "method": "Project manual stating the dictionary and function; extension install script stating the function's volatility.",
  "limitations": "Same page dating as A1-SR-01. The 19 page differs from 18 only in section numbers and the case of SQL keywords in the examples. The manual does not say that unaccent() is STABLE or what that means for index expressions; the script shows STABLE, and the consequence for indexes is inferred from the general rule that index expressions need immutable functions.",
  "provenance": "Pages downloaded with curl on 2026-11-18; unaccent--1.1.sql read from raw.githubusercontent.com on 2026-11-18. Re-verify at the URLs above."
}
```

## Evidence

- Introduction: "unaccent is a text search dictionary that removes accents (diacritic signs) from lexemes. It's a filtering dictionary, which means its output is always passed to the next dictionary (if any), unlike the normal behavior of dictionaries."
- Introduction: "The current implementation of unaccent cannot be used as a normalizing dictionary for the thesaurus dictionary."
- F.48.1: "This file must be stored in $SHAREDIR/tsearch_data/ (where $SHAREDIR means the PostgreSQL installation's shared-data directory)."
- F.48.1: "Any lines containing untranslatable characters are silently ignored, so that rules files can contain rules that are not applicable in the current encoding."
- F.48.1: the standard rules file "translates characters with accents to the same characters without accents, and it also expands ligatures into the equivalent series of simple characters (for example, Æ to AE)."
- F.48.2 example: a configuration `fr` copied from `french` maps `hword, hword_part, word` to `unaccent, french_stem`, so `to_tsvector('fr','Hôtels de la Mer')` gives `'hotel':1 'mer':4`.
- F.48.3: "The unaccent() function removes accents (diacritic signs) from a given string. Basically, it's a wrapper around unaccent-type dictionaries, but it can be used outside normal text search contexts."
- unaccent--1.1.sql: "LANGUAGE C STABLE STRICT PARALLEL SAFE;" for both forms of unaccent().
- What the source shows: unaccent works in two places: as a filtering dictionary inside a text search configuration, and as a plain function. Its rules live in a file on the server's disk, outside the database tables.
- What the source does not show: whether a change to the rules file requires a reindex. Inferred: a tsvector or index built through unaccent holds the old output until it is rebuilt, as A1-SR-14 shows for the 9.6 rules change. The manual does not say how German umlauts map; the rules file itself was not read.
