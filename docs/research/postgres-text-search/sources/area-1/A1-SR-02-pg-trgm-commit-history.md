# A1-SR-02: pg_trgm commit history, 2004 to 2018

```json
{
  "source_identity": "PostgreSQL commits cbfa4092bb9c0668dba9870ca06038aebe71d7e6 (2004-05-31, contrib/pg_trgm/README.pg_trgm), 6e2f3ae8842392c46ccc91a9ce4bba92296890cb (2011-02-01, LIKE and ILIKE), 3ccae48f44d993351e1f881761bd6c556ebd6638 (2013-04-09, regular expressions), f576b17cd6ba653bdace1f0da9a3b57f4984e460 (2016-03-16, word_similarity), 5871b88487cfd07966e2ce08609a4d6d5ee9718e (2016-03-16, threshold setting), be8a7a6866276b228b4ffaa3003e1dc2dd1d140a (2018-03-21, strict_word_similarity); github.com/postgres/postgres",
  "author_or_issuing_body": "Commit authors and committers: Teodor Sigaev, Oleg Bartunov, Tom Lane, Alexander Korotkov, Artur Zakirov",
  "publisher": "PostgreSQL Global Development Group (git repository mirrored at github.com/postgres/postgres)",
  "publication_date": "2018-03-21T11:57:42Z",
  "relevant_event_date": "2004-05-31",
  "source_family": "Primary: the PostgreSQL source repository. The release notes in A1-SR-14 summarise the same changes; the bug thread in A1-SR-03 is the discussion that be8a7a6866 cites.",
  "precise_evidence_location": "Commit messages of the six commits; README.pg_trgm on branch REL8_2_STABLE, sections Definitions and Public Functions",
  "method": "Commit records and the original module README read through the GitHub API.",
  "limitations": "publication_date is the date of the last commit in the set; relevant_event_date is the first. The first commit's message was not read; the README was read at branch REL8_2_STABLE and the date of its earliest commit stands for the module's arrival. Commit messages state intent; they do not show the review discussion except where they link it.",
  "provenance": "Read with gh api repos/postgres/postgres/commits/<sha> and gh api repos/postgres/postgres/contents/contrib/pg_trgm/README.pg_trgm?ref=REL8_2_STABLE on 2026-11-18. Commits found with the GitHub commit search on the terms word_similarity, LIKE ILIKE, regular expression and similarity_threshold."
}
```

## Evidence

- README.pg_trgm (2004): "The pg_trgm contrib module provides functions and index classes for determining the similarity of text based on trigram matching."
- README.pg_trgm: "A trigram is a set of three consecutive characters taken from a string."
- README.pg_trgm, show_limit: "Returns the current similarity threshold used by the '%' operator." The 2004 module sets the threshold with the functions set_limit and show_limit.
- Commit 6e2f3ae (2011-02-01): "Support LIKE and ILIKE index searches via contrib/pg_trgm indexes."
- Commit 6e2f3ae: "Unlike Btree-based LIKE optimization, this works for non-left-anchored search patterns. The effectiveness of the search depends on how many trigrams can be extracted from the pattern."
- Commit 6e2f3ae: "(The worst case, with no trigrams, degrades to a full-table scan, so this isn't a panacea. But it can be very useful.)"
- Commit 3ccae48 (2013-04-09): "This works by extracting trigrams from the given regular expression, in generally the same spirit as the previously-existing support for LIKE searches, though of course the details are far more complicated."
- Commit 3ccae48: "Currently, only GIN indexes are supported. We might be able to make it work with GiST indexes later." The current manual (A1-SR-01) lists regular expressions for both index types; the commit that added GiST support was not looked up.
- Commit f576b17 (2016-03-16): "Patch introduces a concept of similarity over string and just a word from another string."
- Commit 5871b88 (2016-03-16): "Use GUC variable pg_trgm.similarity_threshold insead of set_limit()/show_limit() which was introduced when defining GUC varuables by modules was absent."
- Commit be8a7a6 (2018-03-21): "strict_word_similarity is similar to existing word_similarity function but it takes into account word boundaries to compute similarity."
- What the source shows: the order in which trigram matching gained index support for LIKE, ILIKE and regular expressions, word similarity, the configuration setting for thresholds, and strict word similarity, with the authors' stated reasons.
- What the source does not show: the criticism of word_similarity itself; A1-SR-03 holds it.
