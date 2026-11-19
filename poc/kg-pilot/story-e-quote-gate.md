# Story E: The Quote Check As A Gate

## Goal

Show that the store refuses an extracted decision whose quote is not in the span it cites, whichever script writes it.

## Why this is a candidate

Story D loaded all 66 extracted decisions and only recorded the quote check in the anchor. Seven of the local model's quotes occur nowhere in the input, and an eighth sits in the next span. Each of the eight still points to a real message, so it looks like evidence ([notes on stories C and D](notes-cd.md), open point 2).

## What to build

- `schema.sql`: a function `quote_found(quote, body)` that returns exact, whitespace, or missing, and a trigger on `edge` that refuses a `quotes` edge whose source's quote is missing from the target's text.
- `load_extractions.py`: writes each decision and its edge in one savepoint, so a refused edge leaves no decision behind, and prints each refused decision.
- `test_quote_gate.py`: runs the gate on a throwaway database `kg_gate` and drops it again.

## Definition of done

1. The local extraction loads 29 of 37 decisions: the 28 exact quotes and the 1 that differs only in whitespace.
2. The Claude extraction loads 29 of 29.
3. No decision is left without its `quotes` edge.
4. No loaded `quotes` edge has a missing quote.
5. A direct insert of a `quotes` edge with a missing quote, as the application role, is refused.
6. A second run adds nothing.
