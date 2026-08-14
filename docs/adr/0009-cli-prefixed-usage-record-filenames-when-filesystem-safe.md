---
id: 0009
status: accepted
evaluation: none
---

# `<cli>_<session_id>` as the usage-record filename when filesystem-safe

## Context

ADR-0007 stored usage records and transcript copies under
`filesystem_key(<identifier>)`, which kept only bounded **lowercase** ASCII
components verbatim and digested everything else to a fixed
`opaque-<sha256>` name. Pi root session ids carry uppercase ISO-8601
separators (`2026-…T…Z…`), so they always fell into the digest branch: a
directory listing of `.agent-factory/usage/` showed `opaque-<hash>.jsonl`
for every Pi root run, while Pi subagent ids (`pi-<uuid>`) and bare UUIDs
stayed readable. One id shape per CLI was hidden behind a digest for no
operational benefit.

The digest served two purposes when ADR-0007 was written. The first,
containment (SEC-0001), is real and unchanged: a hostile `session_id`
containing `/`, `..`, or a Windows device name must not redirect writes
outside the usage root. The second, privacy — the pathname should not leak
the session id — does not apply here: `.agent-factory/` is gitignored and
owner-only (`0700`/`0600`), and the raw id is already retained inside the
JSON record body. The privacy rationale was unwarranted, and the case
restriction that enforced it made Pi root records unreadable on disk for no
gain.

This ADR supersedes the identifier-to-path paragraph of ADR-0007 only.
ADR-0007's remaining decisions — one `usage-capture` pipeline with per-CLI
transcript normalizers, fixed `cl100k_base` counts, append-only JSONL
persistence, parent/child conservation semantics, and the generation-fenced
lifecycle/supervisor and runtime-provisioning design — remain in force and
unchanged. ADR-0007 is marked `superseded by ADR-0009` so readers consult
this ADR for the current naming rule; the rest of 0007 is inherited here by
reference. No genuine alternative warranted a Pugh Matrix: containment is a
hard constraint, and the only design freedom was the set of ids kept
verbatim, which this rule defines directly.

## Decision

The session-level storage key is `<cli>_<session_id>`: the record file
is `.agent-factory/usage/<cli>_<session_id>.jsonl` and the transcript
directory is
`.agent-factory/usage/transcripts/<cli>_<session_id>/`. A directory listing
therefore identifies which CLI produced a run at a glance. The CLI token is
itself passed through `filesystem_key`, so a hypothetical hostile CLI value
cannot redirect writes; in practice the four supported CLIs (`pi`,
`claude-code`, `copilot`, `codex`) are all filesystem-safe and pass through
verbatim. The `_` separator is chosen because no supported CLI id contains an
underscore, so the CLI prefix is unambiguous and recoverable by splitting on
the first `_`.

`filesystem_key` keeps a verbatim identifier as a filename component when
the identifier is a single **filesystem-safe** component, and digests it to
`opaque-<sha256>` only when it is genuinely unsafe as a filename. The
safe-component rule is `[A-Za-z0-9][A-Za-z0-9._-]{0,99}`, excluding `.`/`..`,
the `opaque-` prefix, oversized values, and Windows device stems (`con`,
`prn`, `aux`, `nul`, `com1-9`, `lpt1-9`) matched case-insensitively so
allowing uppercase does not let `Com1.txt` slip through verbatim. Mixed case
is permitted, so Pi root ids (`2026-…T…Z…`), Pi subagent ids (`pi-<uuid>`),
and bare UUIDs all keep their readable name on disk.

The transcript leaf inside the session directory stays keyed by `record_id`
alone (no CLI prefix): the directory already carries the CLI, and `record_id`
is per-record (`<session_id>-NNNN`, or a UUID when no session id exists).

Identifiers that are unsafe as a filename component — path separators,
`.`/`..`, Windows device names, oversized, or non-ASCII — still map to a
fixed `opaque-<sha256>` digest, preserving the SEC-0001 containment property
unchanged. The original identifier is retained inside the JSON record body
regardless of which branch the path took.

Existing on-disk records were renamed forward to the `<cli>_<session_id>`
layout (session file, transcript directory, and transcript leaf), and each
record's `transcript_ref.path` was rewritten to the new path so evidence
links stay valid. The change is forward-only: renamed session ids are
unique, so no record duplicates or collides with an existing file.

## Consequences

**Positive**

- A directory listing of `.agent-factory/usage/` is readable and names the
  CLI: every record file is `<cli>_<session_id>.jsonl`, so a glance identifies
  which CLI produced which run.
- The cross-path model attribution from ADR-0007 (BUG-0006) is no longer
  obscured — the filename identifies both the CLI and the session.
- Existing evidence links remain valid after the one-time rename.

**Negative / risks**

- The usage directory listing is invertible: anyone who can list it sees
  session ids and which CLI ran. This is accepted: the directory is gitignored
  and owner-only, and the ids were already present in the record bodies.
- Containment depends on the safe-component rule staying strict. Any future
  loosening (e.g. admitting path separators) would reopen SEC-0001; the
  regression suite pins the current boundary.
