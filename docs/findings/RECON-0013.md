---
id: RECON-0013
source: reconcile-spec
severity: major
category: defect
artifact: docs/05_building_block_view.md#L27,L123,L129; docs/06_runtime_view.md#L156; docs/08_crosscutting_concepts.md#L58; docs/12_glossary.md#L32,L69; factory/docs/factory-guide.md#cli-safety-guardrails
status: resolved
traces: [ADR-0004, ADR-0007]
---

# PreToolUse guardrail and run-step described as "both CLIs" (Claude + Copilot), omitting Codex and Pi

**What is wrong:** The arc42 documentation and the factory guide describe the
`block-dangerous-git` PreToolUse guardrail, and in one place the `run-step`
skill, as if only two CLIs exist — Claude Code and GitHub Copilot CLI. The
code-as-built supports four CLIs, and Codex receives the *same* native
PreToolUse guardrail as Claude Code and Copilot CLI, not merely a usage hook.

Concrete drift locations:

- `docs/05_building_block_view.md` §5.2 and §5.5 — `block-dangerous-git` is
  labelled "PreToolUse hook (both CLIs)" (lines 27 and 123). The §5.5
  "Invoked by" column for the `run-step` skill reads "Claude Code, Copilot CLI
  (LLM-executed)" (line 129), omitting Pi and Codex, under which the skill is
  also installed and invoked.
- `docs/06_runtime_view.md` §6.2.5 — "Both CLIs: Works identically for Claude
  Code and Copilot CLI" (line 156).
- `docs/08_crosscutting_concepts.md` §8.2 — "Receives the command as JSON on
  stdin (both CLIs use the same schema)" (line 58).
- `docs/12_glossary.md` — the **PreToolUse Hook** entry states "Both Claude
  Code and Copilot CLI support this" (line 32), and the **CLI** acronym reads
  "Command-Line Interface (here: Claude Code, Copilot CLI)" (line 69). The
  **CLI-Invoked Agent** entry likewise names only Claude Code and Copilot CLI.
- `factory/docs/factory-guide.md` § CLI safety guardrails — "For Claude Code
  and Copilot CLI this is a native `PreToolUse` hook; for Pi it is a
  project-local extension" and "init-factory symlinks the script into both
  `.claude/hooks/` and `.github/hooks/`". Codex is absent from the guardrail
  description entirely, even though the same guide's Codex-operation and
  usage-capture sections treat Codex as a first-class CLI.

Code reality: `factory/config/hooks/block-dangerous-git.sh` opens with "Shared
PreToolUse guardrail for Claude Code, Copilot CLI, and Codex," reading the
command from `.tool_input.command`, `.toolArgs.command`, or `.tool_input.cmd`
to cover all three. `factory/scripts/init-factory` symlinks
`block-dangerous-git.sh` into `.codex/hooks/` (line 357) and wires it as a
`PreToolUse` entry in `.codex/hooks.json` alongside the capture hooks (line
404: `for event in ("PreToolUse", *CODEX_CAPTURE_HOOK_EVENTS)`). The installed
`.codex/hooks/block-dangerous-git.sh` confirms the wiring. Pi enforces the same
deny list through its `.pi/extensions/block-dangerous-git.ts` extension rather
than a hook.

So "both CLIs" is stale in two ways: it undercounts the hook-based CLIs
(Claude, Copilot, Codex = three) and it ignores that Pi enforces the same
guardrail through a different mechanism. This is terminology drift against
`docs/12_glossary.md`'s own canonical CLI set and against ADR-0007, which
names Claude Code, Copilot CLI, Codex, and Pi as the four runtimes.

**Fix:** Update the affected arc42 chapters, glossary, and the factory guide's
CLI-safety-guardrails section so the PreToolUse guardrail is described as
covering Claude Code, Copilot CLI, and Codex (native hook), with Pi enforcing
the same deny list via its project-local extension. Replace every "both CLIs"
with the accurate set, and update the glossary's **PreToolUse Hook**,
**CLI-Invoked Agent**, and **CLI** acronym entries to name all four CLIs. The
§5.5 `run-step` "Invoked by" cell should read across all four CLIs (or
generically "LLM-executed in any supported CLI"). No code change is required —
the code already implements the four-CLI guardrail; only the documentation
lagged.

## Resolution

Updated the arc42 building-block, runtime, crosscutting, and glossary chapters;
the Factory guide; the PRD; UC-07; UC-08; and the supplementary interface
contracts. They now distinguish the three native-hook runtimes (Claude Code,
GitHub Copilot CLI, and Codex) from Pi's equivalent project-local extension,
and describe `run-step` as available in every supported CLI.

## Verification

A fresh search of canonical specifications and architecture documentation found
no remaining two-CLI guardrail language. `spec-lint` completed with 0 errors
and 0 warnings; `arch-lint` completed with 0 errors and the two pre-existing
parse warnings.
