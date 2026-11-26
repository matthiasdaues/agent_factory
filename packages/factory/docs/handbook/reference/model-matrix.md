---
title: Model matrix
type: reference
status: implemented
order: 30
description: The three tiers, the format of model.conf, its fallback rule, and the commands that check it.
---

# Model matrix

The factory routes work to an AI model by tier, so a cheap task stays cheap and a safety-critical task gets the strongest model available.

| Tier       | Use for                                                                                                          | Cost    |
| ---------- | ---------------------------------------------------------------------------------------------------------------- | ------- |
| `economy`  | Mechanical, well-scoped work with test coverage: a change in one folder, or an authoring task bound by a schema. | Lowest  |
| `standard` | The default: work that spans several folders or has three or more dependencies.                                  | Middle  |
| `strong`   | Risk domains such as security, privacy, and data integrity; safety-critical paths; hard synthesis.               | Highest |

The tier rubric is first-match-wins and lives in [dispatch-contract.md § Tier Rubric](../../../rulebooks/conventions/dispatch-contract.md#tier-rubric).

## `model.conf`

`.agent-factory/config/model.conf` maps each tier to a model id for each CLI, in INI-style `[facts]` syntax:

```ini
[facts]
copilot.economy  = gpt-5.4-mini
copilot.standard = gpt-5.4
copilot.strong   = claude-opus-4-6

pi.economy  = openrouter/anthropic/claude-haiku-4.5
pi.standard = openrouter/anthropic/claude-sonnet-4.6
pi.strong   = openrouter/anthropic/claude-opus-4.8
```

| Setting               | Effect                                                                                                                                                                                                                                                          |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cli.tier = model-id` | One line per CLI and tier. The installer writes a `CONFIGURE-ME` line for each tier of each selected CLI that routes models. OpenCode gets none. Replace each one with a model ID. Add lines for each CLI you use, and leave out tiers you never want to reach. |
| `on_missing = halt`   | When a dispatch asks for a tier with no model for the active CLI, the dispatch stops instead of guessing. So a strong-tier task never falls back to a weaker model in silence.                                                                                  |
| Precedence            | An explicit `--model` flag wins over `model.conf`, which wins over the CLI's own default (FR-K3).                                                                                                                                                               |

`on_missing` applies only when a tier has no row. A row with a value is the model the CLI receives, even when the value is `CONFIGURE-ME`. To let the CLI pick its own default for a tier, delete that tier's row and set `on_missing = auto`. `matrix-lint` reports `MX-EMPTY` as an error for a matrix with no model rows.

The file is git-ignored local configuration, so each developer can keep their own mapping. Edit it directly to pin models, swap providers, or add a CLI.

## Commands

| Command                                                                                | Effect                                                                                                                       |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `.agent-factory/factory/scripts/matrix-lint --matrix .agent-factory/config/model.conf` | Checks the syntax, the required fields, and the form of each model id. Runs on every commit, and an error blocks the commit. |
| `.agent-factory/factory/scripts/openrouter-discover --check`                           | Checks the `pi.*` rows against the OpenRouter catalogue.                                                                     |
| `.agent-factory/factory/scripts/openrouter-discover --suggest`                         | Suggests replacements for the `pi.*` rows.                                                                                   |
