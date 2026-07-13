---
id: RETRO-0003
title: No branch redundancy check before merge/rebase
status: open
severity: minor
category: process
date: 2026-07-13
found_by: session-retrospective
tags: [retro, merge, branch-hygiene]
---

# RETRO-0003: No branch redundancy check before merge/rebase

`feat/guardrail-in-init-factory` was 20+ commits behind dev and its unique content had already been independently re-implemented. The attempted rebase hit conflicts, corrupted the safety hook, and cost ~15 minutes — all for a branch with nothing to contribute.

**Fix:** Before planning a merge or rebase, compare `git log --oneline dev..<branch>` against `git log --oneline <branch>..dev`. If the incoming content is a subset of what dev already has, skip the branch. Document this check in `factory/rulebooks/conventions/branching-policy.md`.
