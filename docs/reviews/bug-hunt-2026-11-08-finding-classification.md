---
type: bug-hunt
title: Bug hunt of finding-classification
date: 2026-11-08
status: defects
reviewer: qa-agent
findings_filed: 4
branch: feature/finding-classification
branch_base: 2e4cd6fb975db9b1bffbfab56696284ebbe66c68
branch_head: 107bd1dee469710ef3eac740bdfbfd56d55e2520
---

# Bug hunt of finding-classification

## Result

The hunt found two major defects, two minor defects, and four notes. Neither major defect is in use, so neither is critical. The first lets a Pi agent set a human field with the ordinary `edit` tool. The second lets `git merge` through during a stop when a marker already exists.

The orchestrator sends BUG-0123 and BUG-0124 to a developer. This review fixed nothing, as its brief requires, so the hunt has no retest cycle yet.

## Scope

The hunt ran the scripts of the feature directly, in scratch repositories under the session scratchpad:

- `guard-human-fields`, with payloads in the formats of Claude Code and Pi.
- `finding-lint`, with malformed finding files and hostile `artifact` values.
- `premerge-check`, `block-dangerous-git.sh`, and the stop notice.
- `init-factory --cli claude codex copilot pi opencode` and `--remove claude pi opencode`. Every link resolved, and the entries of `.claude/settings.json` and `.codex/hooks.json` hold the tools that the contract lists. The removal took the links away.

The argument names of Pi come from the release 1.5.0 installed on this machine.

## Not checked

- The full test suite did not run. The guardrail hook refuses `uv run pytest` under BR-024, and this review did not reword the command to get past the hook.
- The TypeScript tests did not run, for the same reason.
- The acceptance Scenarios did not run, because the project declares no Gherkin runner for this feature (FC-QG02).
- `update-factory` did not run, because it asks for the user's confirmation. `init-factory` of this branch did run, and the contract says `update-factory` calls it.
- No real Codex, Copilot CLI, or OpenCode session ran (FC-QG23, FC-QG24).

## Findings

| Finding                                                                                                                                                                                                                                                                                                                                                                | Artifact                                                    | Category   | Severity | Filed as      |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------- | ---------- | -------- | ------------- |
| The guard does not read `edits[].oldText` of the Pi `edit` tool, so every Pi edit passes. Read that list in `check_call`.                                                                                                                                                                                                                                              | `packages/factory/config/hooks/guard-human-fields:191-210`  | Defect     | major    | BUG-0123      |
| A marker written before a stop still passes the merge gate during the stop. Let the gate ask for the stop.                                                                                                                                                                                                                                                             | `packages/factory/scripts/premerge-check:393-398`           | Defect     | major    | BUG-0124      |
| The guard reads the body of a finding file as frontmatter, so a quoted field at the start of a line is refused. Read only the frontmatter.                                                                                                                                                                                                                             | `packages/factory/config/hooks/guard-human-fields:521-538`  | Defect     | minor    | BUG-0125      |
| The guard starts one git process per word of an interpreter script. A script of 1500 words costs 3.05 seconds, and one of 5000 words costs 11.27 seconds. Skip words that cannot name a guarded path.                                                                                                                                                                  | `packages/factory/config/hooks/guard-human-fields:306-309`  | Defect     | minor    | BUG-0126      |
| A heredoc that writes the blank human fields of the finding template is refused, because the shell pattern reads across the line end and takes the next key as the value. An agent can use `null` or the `Write` tool. This is a shell form, so it stays a note.                                                                                                       | `packages/factory/config/hooks/guard-human-fields:77-79`    | Defect     | note     | `report only` |
| A finding file that is not UTF-8 ends `finding-lint` with a Python traceback and exit 1 in the working-tree mode. The lint still fails closed, and agents write UTF-8.                                                                                                                                                                                                 | `packages/factory/scripts/finding-lint:1104-1111`           | Defect     | note     | `report only` |
| `finding-lint` rejects a list at column zero under a key, which is valid YAML. `mdformat` indents such a list, so a formatted file passes.                                                                                                                                                                                                                             | `packages/factory/scripts/finding-lint:353-379`             | Defect     | note     | `report only` |
| The open case of the code review is closed: a Pi child in a linked worktree loads no project-local extension, because Pi 1.5.0 looks only in `<cwd>/.pi`, and git ignores `.pi/`. So the guard does not block every call there. The guard also does not run there, like every other Pi extension of the Factory, and the comment in `dispatch-wave.ts` says otherwise. | `packages/factory/config/extensions/dispatch-wave.ts:21-23` | Suggestion | note     | `report only` |
