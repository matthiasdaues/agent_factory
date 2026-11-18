# A1-SR-07: ts_rank and ts_rank_cd in the PostgreSQL 18 and 8.3 manual and in tsrank.c

```json
{
  "source_identity": "PostgreSQL 18 manual 12.3.3 Ranking Search Results (https://www.postgresql.org/docs/18/textsearch-controls.html#TEXTSEARCH-RANKING); PostgreSQL 8.3 manual, same section (https://www.postgresql.org/docs/8.3/textsearch-controls.html); src/backend/utils/adt/tsrank.c at commit e3b7f6156916c2ffefb51c12a0576d8b095d5c26 of REL_18_STABLE and commit 1eb1e8b5f366b78d5a0e3821c3a197b7ab0f6ea4 of REL_19_STABLE",
  "author_or_issuing_body": "PostgreSQL Global Development Group; the source comment in calc_rank_or is signed by Oleg Bartunov",
  "publisher": "PostgreSQL Global Development Group, postgresql.org and the git repository",
  "publication_date": "2026-11-12T00:00:00Z",
  "relevant_event_date": "2008-02-04",
  "source_family": "Primary: the PostgreSQL manual and source code. The ranking functions descend from rank and rank_cd in contrib/tsearch2 (A1-SR-13). The cover density method is from Clarke, Cormack and Tudhope (1999), which the manual cites and which was not read.",
  "precise_evidence_location": "18 manual 12.3.3, paragraphs one to three, the normalization list and the paragraph after it, last paragraph; 8.3 manual 12.3.3, same sentences; tsrank.c lines 24-36 (weights and normalization flags), 44-50 (word_distance), 284-345 (calc_rank_or and its comment), 900-940 (calc_rank_cd cover loop)",
  "method": "Project manual stating the functions; source code read for what the functions compute.",
  "limitations": "Same page dating as A1-SR-01; relevant_event_date is the 8.3 release; the two 8.3 sentences quoted below stand unchanged in 18, and the rest of the 8.3 section was not compared. The REL_19_STABLE copy of tsrank.c differs only in the copyright year and memory allocation macros. The statements about inputs are read from function signatures and loops; that the functions use no document frequency or corpus statistics is stated by the manual and matches the code, which reads only the tsvector and the tsquery. The 1999 paper was not read.",
  "provenance": "Manual pages downloaded with curl on 2026-11-18. tsrank.c read from raw.githubusercontent.com at the commits above on 2026-11-18 and diffed between REL_18_STABLE and REL_19_STABLE. Re-verify at the URLs above."
}
```

## Evidence

- 18 manual: "PostgreSQL provides two predefined ranking functions, which take into account lexical, proximity, and structural information; that is, they consider how often the query terms appear in the document, how close together the terms are in the document, and how important is the part of the document where they occur."
- 18 manual: "However, the concept of relevancy is vague and very application-specific."
- 18 manual: "The built-in ranking functions are only examples. You can write your own ranking functions and/or combine their results with additional factors to fit your specific needs."
- 18 manual, ts_rank: "Ranks vectors based on the frequency of their matching lexemes."
- 18 manual, ts_rank_cd: "Cover density is similar to ts_rank ranking except that the proximity of matching lexemes to each other is taken into consideration."
- 18 manual: "This function requires lexeme positional information to perform its calculation." Stripped lexemes are ignored.
- 18 manual: the default weights are `{0.1, 0.2, 0.4, 1.0}` for D, C, B and A. The normalization flags 0, 1, 2, 4, 8, 16 and 32 divide by document length, unique word count, extent distance or rank plus one; flag 0 (the default) ignores document length.
- 18 manual: "It is important to note that the ranking functions do not use any global information, so it is impossible to produce a fair normalization to 1% or 100% as sometimes desired."
- 18 manual: "Ranking can be expensive since it requires consulting the tsvector of each matching document, which can be I/O bound and therefore slow."
- 12.9 of the same manual: "The latter is possible because ranking functions use only local information." (context: partitioning across servers; see A1-SR-10)
- 8.3 manual: "The built-in ranking functions are only examples." and "functions do not use any global information, so it is impossible to produce a fair normalization to 1% or 100% as sometimes desired."
- tsrank.c: "static const float default_weights[NUM_WEIGHTS] = {0.1f, 0.2f, 0.4f, 1.0f};" and "#define DEF_NORM_METHOD RANK_NO_NORM"
- tsrank.c, word_distance: "return 1.0 / (1.005 + 0.05 * exp(((float4) w) / 1.5 - 2));"
- tsrank.c, comment in calc_rank_or: "don't sort for now, just choose maximum weight. This should be corrected"
- What the source shows: both functions score one document against one query from term counts, positions and weight labels in that document's tsvector. They do not use document frequency, collection size or average length, so they are not BM25 and not TF-IDF. Inferred from the code and the manual's statement.
- What the source does not show: any measured retrieval quality, or a core proposal to add collection statistics (searched, not found; see the area index). BM25 extensions belong to area 2.
