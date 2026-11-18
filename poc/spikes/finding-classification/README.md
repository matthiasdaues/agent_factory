# Finding-classification spike

This spike asks whether two raters who apply the finding-classification rules
to the same finding reach the same rating. Raters rate gigacron findings
without their filed rating, and the spike compares the raters with each other
and with the filed rating. It ran on 2026-11-18. The report is
[classification-test-2026-11-18-gigacron.md](../../../docs/reviews/classification-test-2026-11-18-gigacron.md).

## Layout

- [build-blind.py](build-blind.py) builds blind copies of findings from their
  filing commits. It also writes `filing.tsv`, the answer key, and a strip
  log in `key/`.
- [compare.py](compare.py) compares rater pairs with each other and with the
  answer key.
- [key/](key/) holds the filed ratings
  ([answer-key.tsv](key/answer-key.tsv)) and the predictions for run 2,
  written before that run
  ([retest-predictions.md](key/retest-predictions.md)).
- [run-1/](run-1/) holds the first run: 38 findings, three pairs (A, B, C),
  current rulebook.
- [run-2/](run-2/) holds the second run: ten findings, a control pair (K)
  on [rules-1.md](run-2/rules/rules-1.md) and a changed pair (T) on
  [rules-2.md](run-2/rules/rules-2.md).
- [run-3/](run-3/) holds the third run: ATAM-0002, ATAM-0003, and ATAM-0007,
  four raters (Q1 to Q4) on [rules-3.md](run-3/rules/rules-3.md), which adds R1,
  R2, and two draft calibration rows. The results are in
  [run-3-results.md](key/run-3-results.md).
- [run-4/](run-4/) holds the fourth run: the same three findings, four raters
  (E1 to E4) on [rules-4.md](run-4/rules/rules-4.md), which adds a candidate
  rule for exposure. The raters got the handoff's scenario lists in
  `run-4/scenarios/` instead of the handoff. The results are in
  [run-4-results.md](key/run-4-results.md).
- [run-5/](run-5/) holds the fifth run: all 38 findings, rebuilt with
  `build-blind.py`, rated on the rulebook with R1 and R2 by six raters on
  `claude-sonnet-5-5` and six on `gpt-5.6-sol` through `codex exec`. The
  results are in [run-5-results.md](key/run-5-results.md).
- [run-6/](run-6/) holds the sixth run: three designs for the in-use rule
  (`rules-a.md` to `rules-c.md`) on six findings, one of them the invented
  control SPEC-0027, each with two Sonnet and two Codex raters. The results
  are in [run-6-results.md](key/run-6-results.md).
- [run-7/](run-7/) holds the seventh run: design d, a list of named cases
  for `in_use` built from the stakeholder's decisions after run 6, on the six
  findings of run 6. The results are in [run-7-results.md](key/run-7-results.md).
- [run-8/](run-8/) holds the eighth run: design e, the run-7 cases with
  corrected wording, on all 28 document findings with two Sonnet and two Codex
  raters per batch. The results are in [run-8-results.md](key/run-8-results.md).

Each run folder holds the rater brief, `filing.tsv`, the blind copies in
`blind/`, and one JSON-lines file per rater in `out/`.

## Faults in the recorded data

The recorded blind copies were not built with `build-blind.py`, and they carry
faults that the script avoids:

- `run-1/blind/` holds the text at gigacron `dev`, not the filed text.
  ATAM-0006, ATAM-0009, and FAGAN-0003 carry later text and are left out of
  the results.
- `run-2/blind/ATAM-0006.md` holds only the title, and
  `run-2/blind/ATAM-0009.md` lacks its section "Decision for the
  stakeholder".
- `run-2/blind/FAGAN-0003.md` keeps the line "this finding returns to major"
  if its fix story is deferred. A rater can infer from it that the filed
  rating is not `major`.

The briefs were changed when the spike moved here from the session
scratchpad. Their paths now point at this folder, and their read ban became
an allowlist, because the key and the report now sit in this repository.

## Run the test again

1. Build the blind set from the filing commits:

   ```
   python3 -I poc/spikes/finding-classification/build-blind.py \
     <gigacron checkout> poc/spikes/finding-classification/run-4 \
     poc/spikes/finding-classification/key [ID ...]
   ```

   Pass a new run folder. The script adds the filed ratings of the IDs you
   pass to `key/answer-key.tsv` and keeps the other rows.

1. Read `key/run-4-strip-log.md`. It must list only rating fields, resolution
   text, and lines that name a severity. Cut any line that still hints at the
   rating from the blind copy by hand.

1. Copy a brief from `run-1/` or `run-2/` into `run-4/`, and change its paths.

1. Write the predictions into `key/` before any rater starts. Each
   prediction names the result that refutes it.

1. Dispatch two raters per batch, each in a fresh agent, with this prompt:

   ```
   Read and follow the brief at poc/spikes/finding-classification/run-4/brief.md.
   Your rater ID is <ID>. Your batch: <finding IDs>. Report back with the
   short summary the brief asks for.
   ```

1. Compare the pairs:

   ```
   python3 -I poc/spikes/finding-classification/compare.py \
     poc/spikes/finding-classification/run-4 X1,X2 Y1,Y2
   ```

1. Check each rater's transcript for reads outside the allowlist. The gigacron
   handoff `docs/handoff/2026-10-16-folder-architecture.md` names categories
   and one severity. Four raters read it in this spike.

## Limits

All raters ran on `claude-opus-5-5`. The spike shows that the rules give one
model stable results, not that two different reviewers would agree.
