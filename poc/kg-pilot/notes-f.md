# Notes On Story F: A Topic With Two Names

Run on 2026-11-19 against the pilot store of stories B to D. `migrate-to-f.sql` brought the store up to the current schema without dropping data, and ran twice without error.

| Item | Result |
| --- | --- |
| 1. Today's name finds the decisions | Met. 24 decisions through the name "Run Lifecycle", covering 20 of 20 key decisions. |
| 2. The old name finds the same decisions | Met. The same 24 through "Dispatch process". |
| 3. A question naming neither finds no topic | Met. 0 decisions for "What was decided about the release process?". |
| 4. Every decision's span is a message of the session | Met. 24 of 24. |
| 5. Each name quotes the span that first uses it | Met. "dispatch process" at 20:02 on 2026-11-15 in a message of the stakeholder, "Run Lifecycle" at 21:49 the same day. |
| 6. A further load adds nothing | Met. The first load added 31 rows, the second 0. |

`ask.py` now prints the 24 decisions first, in the order they were made, each with its timestamp and message. In story C the same question ranked the handoff 41st.

## Limits

- The route matches a name with `pg_trgm` word similarity, so it needs the name's words in the question in that order. "run-lifecycle decisions" finds the topic. "What did we decide on the lifecycle of a run?", the German "Was wurde zum Dispatch-Prozess entschieden?", and the bare word "dispatch" find none. A question without the name goes through the fused search alone.
- The topic and its two names were set by hand in `load_topic.py`. No extractor proposes topics or names yet.
- The `about` edges come from the blind judge's matches of story D, not from an extractor. They stay candidates.
- The 24 decisions include repeats, because the extractor stated some key decisions twice. The store does not merge them.

## Open points

1. Let the extractor propose a topic and its names for each decision, as candidates, and let a person confirm a renaming.
2. Match names in other word orders and in German, for example with the vector of the name beside its trigrams.
