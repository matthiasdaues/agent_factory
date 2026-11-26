---
title: Git-safety guardrail
type: concept
status: implemented
order: 30
description: Which git commands the guardrail blocks, how each CLI loads it, and what it does not protect against.
---

# Git-safety guardrail

An agent under pressure can route around a failing gate or discard work with one git command. So `init-factory` installs a git-safety guardrail that blocks a fixed list of dangerous git commands before they run. It blocks three groups:

- **Commands that discard or overwrite work or history:** `git push`, `git reset --hard`, `git clean -f` and `-fd`, `git branch -D`, `git checkout .`, `git restore .`, and the fragments `push --force` and `reset --hard` anywhere in a longer command line.
- **Branch creation on its own:** `git branch <name>`, `git switch -c` and `-C`, and `git checkout -b` and `-B`.
- **Commands that skip the repository's own commit gates:** `--no-verify`, `git commit -n`, a new value for `core.hooksPath`, `pre-commit uninstall`, and a `SKIP=...` override on `git commit` or `pre-commit`.

> Rule summary: **MUST**, in an automated run, create every new local branch atomically with its own linked worktree using `git worktree add -b <branch> .current-work/<feature-branch>/<branch> <base>`, and **MUST** verify every new branch-to-worktree mapping with `git worktree list --porcelain` before doing work on that branch.
> Source: [rules.md § Branching](../../../rulebooks/rules.md#branching)

A run by hand checks out each story branch in the primary checkout instead. [Run dispatch by hand](../branches-and-dispatch/run-dispatch-by-hand.md) shows that workflow.

## How each CLI loads it

The guardrail is installed for every project. It is not optional, and it is not a skill you invoke.

| CLI                | Hook path                                                                                           | Configuration                            |
| ------------------ | --------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| Claude Code        | The shared shell script, linked into `.claude/hooks/`                                               | `.claude/settings.json`                  |
| GitHub Copilot CLI | The shared shell script, linked into `.github/hooks/`                                               | `.github/hooks/block-dangerous-git.json` |
| Codex              | The shared shell script, linked into `.codex/hooks/`                                                | `.codex/hooks.json`                      |
| Pi                 | `.pi/extensions/block-dangerous-git.ts`, linked to the factory's extension, with the same deny list | Pi finds it once you trust the project   |

One script serves the three hook-based CLIs. It reads the shell command from the `PreToolUse` JSON shape of each runtime, and Claude Code, Copilot CLI, and Codex treat exit code 2 as "deny". The generated local runtime folders are git-ignored, and so are only the factory's own entries under `.github/`. Your GitHub Actions workflows stay untouched. `init-factory` creates this state again in every clone.

Pi gives weaker protection than the native hook path of the other CLIs. Pi loads project-local extensions only after the project is trusted, and a non-interactive run may ignore them unless the trust is saved or the run is explicitly approved. For stronger protection under Pi, install the same extension globally under `~/.pi/agent/extensions/`, pass it with `pi -e`, or run Pi in a sandbox or container. Pi's own documentation describes its model in the pages on extensions, security, and containerization, under `packages/coding-agent/docs/` of the `earendil-works/pi-mono` repository on GitHub.

## What it does not protect against

The guardrail is a backstop, not a security boundary. It catches an accidental bypass or one made under pressure, such as a background agent that routes around a failing gate. It does not stop a determined bypass. A user with a shell outside the CLI, or anyone who edits the CLI's own configuration, can always get around it.
