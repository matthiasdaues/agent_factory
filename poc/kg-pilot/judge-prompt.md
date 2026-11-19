You judge a measured experiment. You get two files:

- `answer-key.json`: twenty design decisions, numbered 1 to 20, as they were written down at the time.
- `out/pool.json`: decision statements that extractors produced from the conversation, each under a neutral pool id. The order is random. You are not told which extractor wrote which statement.

For each of the twenty decisions, list every pool id whose statement states that decision or a central part of it. A statement matches when a reader who knows only the statement would know that this decision was taken. A statement that only names the topic does not match. One statement may match more than one decision. Many statements may match no decision; that is expected.

Write JSON of this form:

{"matches": [{"number": 1, "pool_ids": ["P004", "P017"]}, ...], "notes": "anything a reader of the scores should know"}

Give all twenty numbers, with an empty list where nothing matches.
