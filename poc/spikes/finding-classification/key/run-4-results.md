# Run 4 results (2026-11-18)

Raters E1 to E4 rated ATAM-0002, ATAM-0003, and ATAM-0007 with
`run-4/rules/rules-4.md`. The predictions are in
[run-4-predictions.md](run-4-predictions.md).

| Rater | ATAM-0002 | ATAM-0003 | ATAM-0007 |
| ----- | ---------------------- | ------------------------------------- | ---------------------- |
| E1 | `fails`, `risk`/major | `uncertain`, `risk`, no severity | `fails`, `risk`/major |
| E2 | `fails`, `risk`/major | `fails`, `risk`/major | `fails`, `risk`/major |
| E3 | `fails`, `risk`/major | `fails`, `risk`/major, low confidence | `fails`, `risk`/major |
| E4 | `fails`, `risk`/major | `uncertain`, `question`, no severity | `fails`, `risk`/major |

| Prediction | Result |
| ------------------------------------- | ------------------------------------------------------------------------------------------- |
| P8: ATAM-0002 `fails`, `major` risk | Held, 4 of 4. |
| P9: ATAM-0003 `uncertain` | Refuted. E2 and E3 gave `fails`. |
| P10: ATAM-0007 `fails` | Held, 4 of 4. |
| P5: `uncertain` gives a `question` | Refuted. E4 filed a `question`. E1 kept category `risk`, with no severity and not blocking. |
| P7: all ratings in architecture class | Held, 12 of 12. |

## What the run shows

- The exposure rule does not decide ATAM-0003. Under `rules-3.md`, all four
  raters gave it `fails`. Under `rules-4.md`, the raters split two to two,
  and the split decides whether the finding blocks. So the rule as worded
  makes the case worse, not better.
- All four raters named the same open point on ATAM-0003: is a boundary tick
  inside a publication part of scenario 7, or an event the scenario does not
  name? The rule names a crash and a timeout as examples. It cannot say
  whether a given event belongs to a given scenario. That is a question about
  the scope of the scenario, and the scenario's owner answers it.
- All four raters named a second open point on ATAM-0002: does a lock that the
  design leaves out count as "an implementation choice that the design leaves
  open"? All four read it as a failure of the design, so the point did not
  change a rating.
- Row 1 reached two raters. E4 applied it fully. E1 dropped the severity and
  the blocking, but kept category `risk`. The row's severity column says
  "none, `question`", and that did not carry the category for E1.
- E1 named one more open point on ATAM-0007: the rule does not cover a design
  that can be read two ways, where each reading fails a different scenario.

## Leaks

The raters read the scenario copies in `run-4/scenarios/` and no handoff. The
tool calls show no read of `docs/findings/`, `docs/reviews/`, `docs/handoff/`,
`key/`, the earlier runs, or another rater's output. E1 ran
`git show --stat` on the filing commits, which lists file names but no
content.
