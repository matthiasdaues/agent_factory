# A1-SR-13: From contrib/tsearch and contrib/tsearch2 to core text search, 2001 to 2008

```json
{
  "source_identity": "contrib/tsearch/README.tsearch on branch REL7_3_STABLE; contrib/tsearch2/README.tsearch2 on branch REL8_2_STABLE; commits b57705673d02483b6e20d8a4d55a8aa182055d08 (2001-10-12, txtidx), b88605337ea37ce1080a696937540cf8b48338d1 (2003-07-21, tsearch2 module) and 140d4ebcb46e17cdb1be43892ed797e5e060c8ef (2007-08-21, tsearch2 to core); PostgreSQL 8.3 manual 12.12 Migration from Pre-8.3 Text Search (https://www.postgresql.org/docs/8.3/textsearch-migration.html)",
  "author_or_issuing_body": "Oleg Bartunov and Teodor Sigaev (tsearch, tsearch2 and the core port); Tom Lane (committer of the core port); PostgreSQL Global Development Group (8.3 manual)",
  "publisher": "PostgreSQL Global Development Group (git repository mirrored at github.com/postgres/postgres; postgresql.org)",
  "publication_date": "2008-02-04T00:00:00Z",
  "relevant_event_date": "2007-08-21",
  "source_family": "Primary: module READMEs and commits in the PostgreSQL repository, and the 8.3 manual. The release notes for 8.3 and 10 (A1-SR-14) summarise the same steps.",
  "precise_evidence_location": "README.tsearch, opening notice and section IMPORTANT NOTICE; README.tsearch2, opening and Main features; commit messages of b57705673d, b88605337e and 140d4ebcb4; 8.3 manual 12.12, list of adjustments",
  "method": "Developer READMEs and commit messages; project manual.",
  "limitations": "publication_date is the 8.3 release date, on which the migration page appeared; relevant_event_date is the core port commit. The READMEs were read at the last branch that carried them, not at their first commit, so their wording may postdate the first release of each module. The OpenFTS project and the tsearch V2 web site at sai.msu.su were not read. No source found states why the project chose to move tsearch2 into core; the commit message gives no reason.",
  "provenance": "READMEs read with gh api repos/postgres/postgres/contents/<path>?ref=<branch> on 2026-11-18; first commits found with gh api commits?path=<file>; 8.3 manual page downloaded with curl on 2026-11-18. Re-verify at the same paths and URL."
}
```

## Evidence

- README.tsearch: "This module is deprecated in 7.4 version of PostgreSQL and will be obsoleted in 7.5. Please, use new tsearch2 contrib module"
- README.tsearch: "Tsearch contrib module contains implementation of new data type txtidx - a searchable data type (textual) with indexed access."
- README.tsearch: "This is a first step of our work on integration of OpenFTS full text search engine (http://openfts.sourceforge.net/) into PostgreSQL."
- README.tsearch: "We didn't try to implement a full-featured search engine with stable interfaces but rather experiment with various approaches."
- Commit b577056 (2001-10-12): "txtidx datatype for full text indexing with GiST."
- README.tsearch2: "Tsearch2 - is the full text engine, fully integrated into PostgreSQL RDBMS."
- README.tsearch2, Main features: "Sophisticated ranking functions with support of proximity and structure information (rank, rank_cd)" and "Index support (GiST and Gin) with concurrency and recovery support"
- README.tsearch2: "OpenFTS is a middleware between application and database."
- Commit 140d4eb (2007-08-21): "Tsearch2 functionality migrates to core. The bulk of this work is by Oleg Bartunov and Teodor Sigaev, but I did a lot of editorializing, so anything that's broken is probably my fault."
- 8.3 manual 12.12: "Text search configuration setup is completely different now. Instead of manually inserting rows into configuration tables, search is configured through the specialized SQL commands shown earlier in this chapter."
- 8.3 manual 12.12: "Configuration files now must be placed in a single specified directory ($SHAREDIR/tsearch_data), and must have a specific extension depending on the type of file, as noted previously in the descriptions of the various dictionary types. This restriction was added to forestall security problems."
- What the source shows: text search went from a GiST-indexed type txtidx in contrib/tsearch (2001), to contrib/tsearch2 with tsvector, tsquery, configuration tables and rank functions (2003), to core in 8.3 (2008). In core, SQL commands replaced the configuration tables, and dictionary files moved to one directory for security.
- What the source does not show: the criticism that drove the move to core; no record states it.
