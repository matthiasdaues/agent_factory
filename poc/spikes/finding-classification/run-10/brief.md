# Brief: blind classification of gigacron findings

## Goal

You classify a batch of review findings with the finding-classification
rules, without seeing the severity they were given. Several raters classify
the same findings independently. The parent session then compares the raters
with each other and with the original severity. So your answers must come from
the rules and the evidence, not from a guess at the original rating.

## Inputs

- The rules: your own rules file, `poc/spikes/finding-classification/run-10/rules/<RULES>`.
  Read it in full before the first finding. It defines the classes, the
  basis fields, the consequence tree, the bug bar, the architecture matrix,
  and the calibration examples.
- The blind findings: `poc/spikes/finding-classification/run-10/blind/<ID>.md`. Severity, category, status,
  and the resolution text are removed.
- The filing commit of each finding: `poc/spikes/finding-classification/run-10/filing.tsv` (ID, full SHA,
  date). Judge every finding as of its filing commit.
- The gigacron repository, read-only:
  `/home/matthiasdaues/Documents/repos/dt_vf/giga-x/gigacron/gigacron`.
  Use it to check `in_use` and to read the artifact a finding names.

## How to check `in_use`

Use only `git -C <repo> log`, `git -C <repo> show <sha>:<path>`,
`git -C <repo> branch --contains <sha>`, `git -C <repo> tag --contains <sha>`,
and `git -C <repo> grep <pattern> <sha>`. Apply the rulebook's § In use:

- A document is in use only when stories or code that exist at the filing
  commit, outside the run that filed the finding, already encode the
  statement. Name that story or code file, or say that none does.
- Code is in use when its lines exist unchanged on `dev`, `main`, a release
  tag, or an installed copy at the filing time.

## Constraints

- Do not read `docs/findings/` in the gigacron repository, at any commit, and
  do not read `docs/reviews/` or `docs/handoff/` there. Those files hold the
  original rating.
  Do not use `git log -p` or `git show` on commits in a way that prints
  finding files.
- Do not change anything in the gigacron repository: no checkout, no switch,
  no stash, no write. Use the read commands above only.
- In this repository, read only this brief, the blind folder, `filing.tsv`,
  and your own rules file. Do not read anything else under
  `poc/spikes/finding-classification/`, and do not read `docs/reviews/`.
  These hold the original ratings and the other raters' output.
- Write only your own output file.

## Output

Write one JSON object per finding, one per line, to
`poc/spikes/finding-classification/run-10/out/<RATER>.jsonl`. Keys:

<!-- yaml-excerpt -->
```
{"id": "SPEC-0001", "review_class": "document", "category": "defect",
 "type": "inconsistent", "basis": {"in_use": false, "harms_downstream": false,
 "fails_purpose": true, "raises_cost": true}, "severity": "major",
 "blocking": true, "in_use_evidence": "No story or code at 2ed84b9 encodes ...",
 "why": "One sentence that names the deciding answer and the concrete consequence.",
 "confidence": "high"}
```

- The `basis` keys follow the class: the four tree fields for document, code,
  and runtime; `effect`, `second_breach`, `trusted_access`, `non_default`,
  `user_action`, `confidence`, `in_use`, plus `rating` for security;
  `importance`, `exposure`, `in_use` for architecture.
- A `question` gets `severity: null` and `blocking: false`.
- `confidence` is `high`, `medium`, or `low`: how sure you are of the
  deciding answer. Use `low` when the rules let two answers stand.
- For a document-class finding, add a key `in_use_case` with the name of
  the case of § In use that decided `in_use`. When the Fix offers options,
  give one name per option, separated by commas.
- For a document-class finding, add a key `side_text` with `omission`,
  `false`, or `none`, as § Class: document defines a side text.
- Add a key `rule_gap` with one sentence when the rules did not settle the
  case, and name the rule text that left it open. Leave it out otherwise.

## Report back

Reply in at most ten lines: the count of findings classified, the count per
severity, and each `rule_gap` in one line. Do not restate the JSON.

## Stop conditions

Stop and report when the rulebook or a blind file is missing, or when a
finding cannot be classified without reading the forbidden files.
