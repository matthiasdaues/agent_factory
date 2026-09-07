---
id: RETRO-0002
title: Safety hook traps user when it contains conflict markers
status: open
severity: major
category: reliability
date: 2026-07-13
found_by: session-retrospective
tags: [retro, safety-hook, conflict, git]
---

# RETRO-0002: Safety hook traps user when it contains conflict markers

During a rebase of `feat/guardrail-in-init-factory`, merge conflicts left `<<<<<<<` markers inside `block-dangerous-git.sh`. The corrupted script then blocked ALL git commands — including the cleanup commands needed to recover (`git reset --hard`, `git rebase --abort`). Recovery required manual file editing and low-level git plumbing (`git read-tree`, `git checkout-index`).

**Fix:** Add a self-check at the top of `block-dangerous-git.sh`: if the script's own source contains `<<<<<<<`, print a warning to stderr and exit 0 (fail open). A hook that prevents its own repair is a trap, not a guardrail.
