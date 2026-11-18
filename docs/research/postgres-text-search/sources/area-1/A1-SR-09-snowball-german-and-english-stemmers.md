# A1-SR-09: Snowball project, German and English (Porter2) stemming algorithms

```json
{
  "source_identity": "Snowball, 'German stemming algorithm' (https://snowballstem.org/algorithms/german/stemmer.html) and 'The English (Porter2) stemming algorithm' (https://snowballstem.org/algorithms/english/stemmer.html)",
  "author_or_issuing_body": "Snowball project (Martin Porter and later maintainers)",
  "publisher": "snowballstem.org",
  "publication_date": "2026-11-18T00:00:00Z",
  "relevant_event_date": "2002-09-01",
  "source_family": "Primary for the algorithms that PostgreSQL ships as its german and english dictionaries (A1-SR-08); not a PostgreSQL source.",
  "precise_evidence_location": "German page: the paragraphs after the vocabulary sample, section Compound words, section History of functional changes to the algorithm, and the step that maps ae, oe and ue. English page: section Developing the English stemmer and its history list",
  "method": "Algorithm descriptions written by the algorithm authors, with sample vocabularies.",
  "limitations": "The pages carry no single date; publication_date is the retrieval date. relevant_event_date is the September 2002 revision of the English page (month only, set to the first day). The pages do not date the Snowball 3.0.0 release; that PostgreSQL 19 contains the 3.x rules is inferred from the 2025-12-15 sync commit (A1-SR-08) and the 19 release note (A1-SR-14). No retrieval quality figures are given.",
  "provenance": "Pages downloaded with curl on 2026-11-18 and converted to text. Re-verify at the URLs above."
}
```

## Evidence

- German: "Despite its inflexional complexities, German has quite a simple suffix structure, so that, if one ignores the almost intractable problems of compound words, separable verb prefixes, and prefixed and infixed ge, an algorithmic stemmer can be made quite short."
- German: "The umlaut in German is a regular feature of plural formation, so its removal is a natural feature of stemming, but this leads to certain false conflations"
- German, Compound words: "To split up compound words cannot be done without a dictionary, and the purely algorithmic stemmers presented here do not attempt it."
- German, Compound words: "We would suggest, however, that the need for compound word splitting in these languages has been somewhat overstated."
- German: "As with the other stemmers, words are assumed to be lower cased before stemming. This potentially loses information since nouns are always capitalised in German"
- German, history: "Snowball 3.0.0: Handle ASCII transliterations of umlauts (merging the" and the list goes on to name the former german2 variant. Note: the full line holds its own quotation marks; the quote stops before them.
- German, history: "Snowball 2.0.0 (2009-12-11): Extra rule for -nisse ending added"
- English: "But it is hardly surprising that after twenty years of use of the Porter stemmer, certain improvements did suggest themselves, and a new algorithm for English is therefore offered here."
- English history lists Snowball 3.0.0 changes, for example "Snowball 3.0.0 Avoid conflating emerge with emergency."
- What the source shows: the german stemmer strips suffixes and folds umlauts, and does not split compounds. Porter2 replaced the original Porter stemmer for English. Both algorithms changed in Snowball 3.0.0, so stems differ between PostgreSQL 18 and 19 (A1-SR-14).
- What the source does not show: how PostgreSQL's german configuration handles hyphenated compounds; that depends on the parser's hword tokens (A1-SR-06), which was not traced further.
