---
name: init-factory
description: Wire Agent Factory into a project — new or existing — by running the deterministic init-factory script and relaying its result. Invoked explicitly, never automatically.
category: utility
disable-model-invocation: true
---

# Init Factory

A thin wrapper around `factory/scripts/init-factory` — a normal, standalone, idempotent Python script that does all the actual work (git init, dot-dir symlinks, `.gitignore`/`.pre-commit-config.yaml` merging, `pre-commit install`). It is built to two promises: it never disturbs what the project already owns, and everything it adds is reversible without a trace via its companion `factory/scripts/remove-factory`. This skill exists only for CLIs that want to trigger it conversationally; **the script itself needs no AI in the loop at all** — running it directly from a shell works exactly the same way. Use whichever is convenient.

**Bootstrap note.** Before this has ever run against a project, there is no `.claude/skills/` or `.github/skills/` yet for a CLI to resolve this skill by name — that's the whole point of running it. The very first invocation has to name the file directly (e.g. "read `factory/skills/init-factory/SKILL.md` in the agent_factory checkout and follow it"), not rely on skill-name resolution. Every later invocation, in a project that already has `factory/` installed, can be a normal by-name skill call.

## Step 1 — Locate the script and confirm the target

Find `factory/scripts/init-factory` — either inside this project's own `factory/` (already initialized once) or, on a first-ever run, inside the agent_factory checkout the user pointed you at.

State plainly what's about to happen before running anything: the target directory (default: current directory — confirm this is right, don't assume), whether it's a fresh directory or an existing repo, and that this will run `git init` (if needed), create symlinks, and modify `.gitignore` / `.pre-commit-config.yaml`. Wait for confirmation — this mutates repo state and is exactly the kind of action that warrants a check first, not a courtesy skip.

## Step 2 — Run it

```bash
factory/scripts/init-factory --target <confirmed target> [--source <agent_factory checkout, if not already inside one>]
```

Do not pass flags the script doesn't have, and do not try to reimplement any of its steps by hand (writing symlinks yourself, hand-editing `.pre-commit-config.yaml`) — the whole point of the script is that its idempotency and collision checks are deterministic; redoing them by hand reintroduces the variance this design avoids.

## Step 3 — Relay the result, verbatim in substance

The script prints one line per step: created, already-present-skipped, linked, or skip-already-linked. Report it plainly, not compressed into "done" — the fresh-vs-existing distinction per step is the useful information (e.g. "your existing `.pre-commit-config.yaml` hooks were preserved, Agent Factory's were merged in alongside them").

Exit code 1 means the script stopped on a genuine collision or an unmerge-able `.pre-commit-config.yaml` — its stderr names the exact path and reason. Report that error as-is and stop. Do not attempt to resolve the collision yourself (deleting or moving the colliding file/symlink) without being explicitly asked to — it may be the user's own content.

**Completion**: the script's own exit code and full output have been relayed; if it exited 0, the project is wired up and `pre-commit install` has run; if it exited 1, the exact blocking path has been reported and nothing further was attempted.
