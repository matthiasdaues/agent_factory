# Usage capture: redundant transcript copies, capture ordering, and lost execute bits

This write-up reports three defects in the usage capture of Agent Factory
1.13.0 and proposes one fix for each. A fourth part describes a one-time
migration for existing installations. All findings come from the gigacron
installation. Line numbers refer to the installed copy under
`.agent-factory/factory/scripts/`.

## Summary

| #   | Defect                                                          | Effect                                                      | Fix                                                                       |
| --- | --------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------- |
| 1   | Each capture stores the full cumulative transcript again        | 9.4 GB of copies where 0.55 GB carry all the text           | Store each chain once; each capture appends its turn and records its span |
| 2   | The session key contains the capture time                       | Every capture opens a new session file; order is lost       | Make the session key stable for the life of a session                     |
| 3   | `_repair_private_tree` sets every file under `usage/` to `0600` | `usage-query` and `usage-explore` fail: `Permission denied` | Keep the execute bit, as `_secure_runtime_tree` does                      |
| 4   | Existing installations hold the redundant copies                | Disk space stays used after the fix                         | One-time migration that turns each chain into one file with turn spans    |

Defect 2 must be fixed before or together with defect 1. The fix for
defect 1 needs a stable file path for each chain and a reliable capture
order, and defect 2 provides both.

## 1. Redundant transcript copies

### Finding

A Claude Code `Stop` record is a cumulative snapshot of the main
transcript. Each capture copies the full normalized text under
`.agent-factory/usage/transcripts/`, plus a `.structured.jsonl` file about
five times larger. A later copy therefore repeats every earlier copy of
the same transcript.

Measured in gigacron on 2026-11-23:

| Copies                            | Stored today | Needed after deduplication |
| --------------------------------- | ------------ | -------------------------- |
| Plain (`*.jsonl`)                 | 1.58 GB      | 0.14 GB                    |
| Structured (`*.structured.jsonl`) | 7.81 GB      | 0.41 GB                    |

One session, `74189bbb…`, has 253 plain copies with 677 MB in total. Its
last copy is 5.7 MB. A byte comparison shows that a copy from the middle of
the session is an exact prefix of the last copy.

### Goal

The capture stores each transcript once and keeps track of its individual
turns. The span of a record is the turn that its capture added.

### Fix

A chain is the sequence of captures of one transcript: the root transcript
of a session, or the transcript of one subagent. Each chain has one
transcript file. Its path stays the same for the life of the chain.

A capture works as follows:

1. It reads the current transcript from the CLI.
2. It checks that the stored chain file is a byte prefix of the current
   transcript.
3. **Prefix holds.** The capture appends the remaining bytes to the chain
   file. The record gets the span from the old file length to the new file
   length.
4. **Prefix does not hold.** The CLI has rewritten the transcript, for
   example by compaction. The capture starts a new chain file and stores
   the full current transcript there. The record gets the span from 0 to
   the file length. A failed check costs disk space, never text.

The same rule covers the plain copy and the structured copy. Each file gets
its own span, because the two files have different byte lengths.

Both the chain file and the record file only grow. No capture changes an
existing line or an existing byte. The raw usage spool therefore stays
append-only, as the architecture requires.

### The span object

A span is a new object in `transcript_ref`. It does not reuse the existing
string field `span` (`usage-capture:446`), whose only value is
`"content-omitted"` (`usage-capture:749`). That marker stays as it is.

- A span is a byte offset range into the chain file. Offsets start at 0.
- The range is half-open: `start` is the first byte, and `end` is the first
  byte after the span. The length is `end − start`. A reader takes
  `data[start:end]` without adjustment.
- The spans of one chain line up without gaps. The `start` of capture *k*
  equals the `end` of capture *k−1*. The first capture of a chain has
  `start = 0`.
- The transcript as it stood at capture *k* is the range from 0 to the
  `end` of capture *k*.
- The token count of a turn is the difference between the cumulative token
  counts of two consecutive records. No extra field is needed.

Example of a record after the fix:

```json
"transcript_ref": {
  "path": ".agent-factory/usage/transcripts/<session-key>/<chain>.jsonl",
  "span": null,
  "byte_range": {"start": 5601200, "end": 5677793},
  "structured_path": ".agent-factory/usage/transcripts/<session-key>/<chain>.structured.jsonl",
  "structured_byte_range": {"start": 27904110, "end": 28286417}
}
```

The field names and the chain file names are a proposal. The maintainer
decides the final names.

### Concurrency

Captures run in detached supervisors and can overlap within one session.
The prefix check and the append must run under the session's reservation
lock and in reservation order. Otherwise two captures can append the same
bytes twice, or append them out of order. This depends on defect 2.

A crash during the append can leave a partial tail in the chain file with
no record pointing to it. The next capture detects the tail, because the
file then no longer ends at the `end` of the last record. The capture
truncates the file to that `end` before it appends.

## 2. The session key contains the capture time

### Finding

`_session_key` (`usage-capture:138`) prefixes the key with
`_timestamp_prefix`. That prefix is set when the storage object is created
(`usage-capture:136`), which happens once per capture. Each capture
therefore opens a new session file and a new transcript directory, for
example:

```
2026-10-16T12-45-11_claude-code_fe14aa7b-e9e6-4605-b36e-43ca990ed04c.jsonl
2026-10-16T13-01-33_claude-code_fe14aa7b-e9e6-4605-b36e-43ca990ed04c.jsonl
```

Each new session file is empty, so `next_sequence_estimate` returns 1 every
time. All 2,105 records in gigacron end in `-0001`. The factory guide says
that the numeric reservation sequence determines the snapshot order. With a
sequence that never passes 1, that guarantee does not hold. The only order
left is `recorded_at`, which has a resolution of one second.

### Fix

The session key must stay the same for the whole life of a session. Use
the CLI name and the session ID, without the capture time. If the
timestamp prefix exists for sorting, take it from the first capture of the
session and keep it.

## 3. `_repair_private_tree` removes execute bits

### Finding

`initialize_usage_lifecycle` calls `_repair_private_tree(usage)`
(`init-factory:3892`). The function (`init-factory:3825`) walks the whole
`.agent-factory/usage/` tree and sets every regular file to `0600`.

The usage-analysis component is installed inside that tree, at
`.agent-factory/usage/analysis/`. After an `init-factory` or
`update-factory` run, every file in `analysis/.venv/bin/` has mode
`-rw-------`, including `python` and `usage-query`. `usage-query` and
`usage-explore` then fail:

```
error: Failed to query Python interpreter at `.../.agent-factory/usage/analysis/.venv/bin/python`
  cause: Permission denied (os error 13)
```

The capture runtime at `.agent-factory/usage/runtime/bin/python` still has
its execute bits in gigacron. The reason is not known yet.

### Fix

`_secure_runtime_tree` (`init-factory:1461`) already shows the intended
rule. It sets an executable file to `0700` and every other file to `0600`.
`_repair_private_tree` should apply the same rule. Skipping `analysis/` and
`runtime/` is a second option, because both trees are managed by their own
install steps.

A test should check that `usage-query --help` still runs after a second
`init-factory` run.

## 4. Migration for existing installations

The stored copies hold enough data to rebuild every turn span. The newest
copy of a chain contains all its turns. The length of each older copy marks
where its turn ends. A one-time migration processes each session as
follows:

1. Collect all capture directories of the session and order them by
   `recorded_at`.
2. Place each non-empty copy into the chain whose last copy is a byte
   prefix of it. If no chain fits, the copy starts a new chain.
3. For each chain, move the newest copy to the chain file path.
4. Give each record of the chain the span from the length of the previous
   copy to the length of its own copy. The first record starts at 0.
5. Delete the older copies.
6. Do the same for the structured copies.

Step 4 changes existing record lines. That is the one exception to the
append-only rule, and only the migration makes it. The migration writes each
record file to a temporary file and renames it into place. A crash then
leaves either the old file or the new file, never a mix. The migration
deletes the older copies only after the rename has succeeded.

The first dry run over gigacron counted plain and structured chains apart.
It gave this result:

|                                   | Plain copies | Structured copies |
| --------------------------------- | ------------ | ----------------- |
| Non-empty copies                  | 1,524        | 1,012             |
| Chains                            | 203          | 104               |
| Sessions with more than one chain | 15           | 8                 |
| Chains that mix agents            | 14           | 3                 |

The migration must handle three cases:

- **Several chains per session.** A `SubagentStop` record carries the
  parent's session ID, but its copy holds the subagent's own transcript.
  A sort by time alone interleaves the chains and breaks the prefix check.
  The first dry run, which sorted by time only, found 192 such breaks.
- **Chains that mix agents.** Some chains contain copies from different
  agents. Copilot and Codex hand a child hook the main transcript, so a
  child record of these CLIs points at a copy of the main transcript. A
  chain is one transcript, not one agent. The migration matches copies by
  content alone and reports each session with such a chain.
- **Rewritten main transcripts.** A copy without an agent that fits no
  chain is the main transcript after the CLI rewrote it. The capture keeps
  such a transcript as one chain and starts a new generation file, so the
  migration does the same. The analysis then counts the main transcript
  once.
- **Empty copies.** 581 copies are empty. Their records show zero tokens
  and `usage_capability: unavailable`. They have no text and get no span.

The migration must hold the same locks as a capture and must not run while
captures are pending.

## Implementation

The fixes are BUG-0139, BUG-0140, and BUG-0142. Three points differ from the
proposal above.

- **The record names its chain.** The analysis keeps the latest snapshot per
  `(cli, session_id, record_id)`. Every record in gigacron ends in `-0001`,
  so all captures of a session collapse into one run, and the subagent
  records drop out. A stable session key would make each cumulative
  snapshot its own run instead. The record therefore gets the field
  `chain`, and the analysis keeps the latest snapshot per
  `(cli, session_id, chain)`. The capture lifecycle passes the stem of the
  CLI's transcript file as the chain name, because the staged copy has a
  random name.
- **The session lock is a file lock.** The capture had no lock before. It
  reserved a record by creating its copy exclusively. The reservation now
  takes a file lock on `transcripts/<session-key>/.lock` and holds it until
  the record is written.
- **The migration links before it deletes.** `migrate-usage-transcripts`
  hard-links each newest copy to its chain file path, renames the new record
  file into place, and only then deletes the old files. A crash leaves the
  references of either the old or the new layout valid. The default is a dry
  run, and `--apply` changes files.

## Dry run and test apply on 2026-11-23

The dry run over gigacron took 30 seconds:

|                             | Result              |
| --------------------------- | ------------------- |
| Sessions                    | 202, all migratable |
| Records                     | 2,105               |
| Chains                      | 221, in 307 files   |
| Captures without text       | 289                 |
| Transcript bytes            | 9.40 GB to 0.55 GB  |
| Sessions with a mixed chain | 11, all Copilot     |

The apply step then ran on a hard-link copy of the gigacron usage folder. An
independent check compared every migrated span with the untouched original
copy. All 2,536 non-empty copies equal bytes 0 to `end` of their chain file.
The usage analysis reads all 2,105 records without a failure.

The session totals of Codex, Copilot, and Pi stay the same. The Claude Code
total rises from 4,395,068 to 11,129,587 tokens. The main chains add up to
the old 4,395,068. The subagent chains add the 6,734,519 tokens that the
collapsed runs had dropped.

## Open questions

- Why does the capture runtime keep its execute bits while the analysis
  environment loses them?
- Why do 581 captures record no tokens? All 581 are `claude-code` records
  of a Copilot session: the Claude Code hook also runs on a Copilot stop and
  hands the Copilot transcript to the Claude Code normalizer. BUG-0143
  tracks the fix and the open question of why Copilot runs that hook.
