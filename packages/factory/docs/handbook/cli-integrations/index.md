---
title: CLI integrations
type: concept
status: implemented
order: 80
description: How the supported CLIs run agents and guardrails, and how to add or remove a CLI.
---

# CLI integrations

The factory works with several AI coding CLIs. This chapter explains how they differ and how to wire one in or out.

<!-- handbook-index:start -->

## Concepts

- [How each CLI runs an agent in its own session](separate-sessions.md): How Claude Code, Copilot CLI, Codex, and Pi start an agent in a separate session, and how Pi runs a parallel wave.
- [Codex](codex.md): What init-factory installs for Codex, which permissions the generated agents inherit, and why you approve the hooks yourself.
- [Git-safety guardrail](guardrails.md): Which git commands the guardrail blocks, how each CLI loads it, and what it does not protect against.

## How-to guides

- [Add or remove a CLI](add-or-remove-a-cli.md): Wire a CLI into an existing installation, or remove one, without running the full installer again.

<!-- handbook-index:end -->
