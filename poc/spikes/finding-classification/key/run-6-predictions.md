# Run 6 predictions, written before the run (2026-11-18)

Run 6 tests three designs for one rule: when a story or code encodes the
statement of a document. The aim is that raters on `claude-sonnet-5-5` and
on `gpt-5.6-sol` reach the same `in_use`. In run 5, they split on SPEC-0013,
SPEC-0014, SPEC-0015, and RECON-0001.

Each design adds one paragraph after R1 in § In use:

- `rules-a.md`, same text: for each option of the Fix, a story or code
  encodes the statement when it states or does what the option's changed text
  says now. A link, a name, or a deferral does not count. Any option counts.
- `rules-b.md`, rework: a story or code encodes the statement when at least
  one option of the Fix forces a change to it.
- `rules-c.md`, quote pair: `in_use: true` needs a quote of a line that the
  Fix changes and a quote of a story or code line that says or does the same.

Six findings: the four that split in run 5, SPEC-0007 as a negative control,
and SPEC-0027 as a positive control. SPEC-0027 is invented for this run. It
uses the facts of SPEC-0015 at 59b6757171a5bdd10f2fe2740fb2a0453684bef7, with
a Fix that has one option and rewrites the line that the delivered code
implements. Each design goes to two Sonnet raters and two Codex raters.

My reading of `in_use` under each design:

| Finding    | a     | b     | c     | Why                                                                                                                        |
| ---------- | ----- | ----- | ----- | -------------------------------------------------------------------------------------------------------------------------- |
| SPEC-0007  | false | false | false | R1: no tool reads the Gherkin syntax.                                                                                      |
| SPEC-0027  | true  | true  | true  | The code does what line 207 says, and the Fix changes both.                                                                |
| SPEC-0013  | false | false | false | The stories defer to T-0052 but do not restate its schema, and the Fix changes only the todo items and a comment.         |
| SPEC-0014  | false | true  | false | No option changes text that the code does. Option 2 makes a story replace the delivered route, which is a forced change. |
| SPEC-0015  | true  | true  | true  | Option 2 marks the field-code paragraph, which the code does, as delivered code that T-0057 replaces.                     |
| RECON-0001 | false | false | false | The Fix changes the scope map and the QA row and adds new code. No existing story or code changes.                        |

Predictions:

- P14: under each design, the four raters agree on `in_use` for all six
  findings. A split on any finding refutes P14 for that design.
- P15: the raters' `in_use` matches the table above. A value that the four
  raters agree on but that differs from the table counts against my reading
  of the design, not against alignment.
- P16: the positive control gives `in_use: true` and the negative control
  `false` under every design. A design that fails either control is rejected,
  whatever its agreement.
- P17: under each design, Sonnet and Codex agree on severity for SPEC-0013,
  SPEC-0014, and SPEC-0015. RECON-0001 also split on `fails_purpose` in run
  5, so the designs need not align its severity.

My guess, which the run can refute: design c aligns best, because it asks
for a fact that a second rater can check.

Known weaknesses:

- SPEC-0027 shares its facts with SPEC-0015, and both are in the same batch.
  A rater may compare the two.
- Two raters per model and design is a small sample.
