---
schema_version: 2
title: Multi-Provider Model Discovery
status: draft
owner: md@matthiasdaues.de
created: 2026-09-07
updated: 2026-09-07
supersedes:

impact:
  scope: single_component
  architecture_change: false
  external_contract_change: false
  boundaries:
    - factory/scripts/model-discover
    - factory/scripts/openrouter-discover
    - factory/agents/virgil.md
    - config/model.conf

governance:
  assurance: standard
  risk_domains:
    - compatibility
    - operations

estimate:
  as_of: 2026-09-07
  basis: judgment
  confidence: low
  human_review_hours:
    min: 0
    max: 0
  normalized_tokens:
    min: 0
    max: 0
---

# Multi-Provider Model Discovery

## Problem

`config/model.conf` maps agent tiers (economy / standard / strong) to
concrete model IDs, per CLI. Today it ships with `CONFIGURE-ME`
placeholders. The user must know which models their provider offers,
which model IDs to use, and how price and capability map to tiers. This
is a cold-start problem — the user needs to know the answer before they
have the tools to find it.

`openrouter-discover` solves this for one provider (OpenRouter) and one
CLI (Pi). But Pi can run on any provider — Anthropic direct, OpenAI
direct, Together, Groq, Fireworks, self-hosted vLLM, LiteLLM. And the
other CLIs (Claude Code, Copilot, Codex) have their own provider
relationships. There is no generic mechanism to query what models are
available and suggest tier assignments.

## Proposed solution

A single `model-discover` script that queries any LLM provider's model
catalog and suggests tier assignments for `model.conf`.

### Provider abstraction

Most LLM providers expose an OpenAI-compatible `/v1/models` endpoint.
Anthropic uses a different shape. The script handles both through a
small provider registry.

| Provider     | Base URL                     | Key env var              | API shape           |
| ------------ | ---------------------------- | ------------------------ | ------------------- |
| `anthropic`  | `api.anthropic.com`          | `ANTHROPIC_API_KEY`      | Anthropic-specific  |
| `openai`     | `api.openai.com`             | `OPENAI_API_KEY`         | OpenAI `/v1/models` |
| `openrouter` | `openrouter.ai/api`          | `OPENROUTER_API_KEY`     | OpenAI-compatible   |
| `together`   | `api.together.xyz`           | `TOGETHER_API_KEY`       | OpenAI-compatible   |
| `groq`       | `api.groq.com/openai`        | `GROQ_API_KEY`           | OpenAI-compatible   |
| `fireworks`  | `api.fireworks.ai/inference` | `FIREWORKS_API_KEY`      | OpenAI-compatible   |
| `mistral`    | `api.mistral.ai`             | `MISTRAL_API_KEY`        | OpenAI-compatible   |
| raw URL      | as given                     | `MODEL_DISCOVER_API_KEY` | OpenAI-compatible   |

A raw URL covers self-hosted setups (vLLM, LiteLLM, Ollama) without
changing the script.

### Modes

```
model-discover --provider openrouter --suggest
model-discover --provider anthropic --list --min-context 100000
model-discover --provider https://my-vllm.internal/v1 --suggest
model-discover --check --cli pi
```

- `--suggest` — query the catalog, rank by price and capability, emit
  advisory `<cli>.<tier> = <model-id>` rows for `model.conf`.
- `--list` — dump the filtered catalog (price, context length, model ID).
  Filterable by `--min-context`, `--max-price`.
- `--check` — validate existing `model.conf` entries against the live
  catalog. Exit 1 on drift.

### Tier suggestion heuristic

The ranking uses prompt price as the primary axis, filtered by minimum
context length:

- **economy** — cheapest model above the context floor.
- **standard** — median-priced model.
- **strong** — most expensive model (assumed most capable).

This is deliberately rough — the same heuristic `openrouter-discover`
uses today. The user confirms or overrides during the fitting. A
capability-based ranking (benchmarks, known model families) is a
possible refinement but adds maintenance burden and stale-data risk.

For providers with small catalogs (Anthropic: ~6 models), the heuristic
simplifies to a hardcoded mapping based on known model families:

- **economy** → haiku-class
- **standard** → sonnet-class
- **strong** → opus-class

### Relationship to `openrouter-discover`

`openrouter-discover` becomes either:

- **Option A** — a deprecated alias that calls `model-discover --provider openrouter`. Thin wrapper, backward compatible.
- **Option B** — absorbed into `model-discover`. The `--check` and `--suggest` flags work the same, the `--provider` flag replaces the implicit OpenRouter assumption.

Option B is cleaner. The pre-commit hook that calls `openrouter-discover --check` would change to `model-discover --check --cli pi --provider openrouter`.

### Integration with VIRGIL fitting step 0

VIRGIL's fitting step 0 (configure the model matrix) gains an automated
path:

1. Read `config/model.conf`. Identify CLIs with `CONFIGURE-ME` placeholders.
2. For each CLI, determine or ask which provider it uses.
3. Run `model-discover --provider <x> --suggest`.
4. Present the suggestions. Let the user confirm, adjust, or override.
5. Write confirmed entries to `model.conf`.

If the provider's API key is not set or the catalog is unreachable,
fall back to manual entry — the fitting step works either way.

### Provider-to-CLI mapping

Which provider serves which CLI is not always fixed:

- **Claude Code** → always Anthropic (the CLI routes through Anthropic's
  API regardless of user configuration).
- **Copilot** → always GitHub (model selection is GitHub-managed, but the
  factory dispatcher needs model IDs for the models GitHub exposes).
- **Pi** → user-configured. Could be OpenRouter, Anthropic direct, OpenAI
  direct, or any compatible endpoint.
- **Codex** → always OpenAI (unless using Azure OpenAI, which has its own
  endpoint).

For Pi, the provider must be configured or asked. For the others, the
provider is implicit from the CLI.

A `provider` field in `model.conf` could make this explicit:

```ini
[providers]
claude  = anthropic
copilot = github
pi      = openrouter
codex   = openai
```

This is optional — `model-discover` can accept `--provider` per
invocation without storing it. But persisting it makes `--check` and
VIRGIL's step 0 self-driving.

## Constraints

- No third-party dependencies (stdlib only, ADR-0006).
- Network access confined to user-invoked discovery, never at dispatch
  time (`resolve-model` stays offline and static).
- API keys are read from environment variables, never stored in
  `model.conf` or any tracked file.
- The script is an operator aid, not a runtime dependency. If discovery
  fails, manual configuration still works.

## Open questions

1. **Should `model.conf` carry a `[providers]` section?** Pro: makes
   `--check` and fitting self-driving. Con: adds a new section to a
   file that currently has only `[facts]` and `on_missing`. The
   `matrix-lint` parser would need updating.

2. **How to handle provider-specific model ID formats?** OpenRouter uses
   `openrouter/<vendor>/<model>`. Anthropic uses bare model IDs
   (`claude-sonnet-4-6`). The script must emit IDs in the format the
   CLI's resolver expects.

3. **Copilot model catalog access** — GitHub's model marketplace has an
   API, but it's not clear whether it exposes a `/v1/models`-compatible
   endpoint. May need a GitHub-specific adapter or hardcoded defaults.

4. **Anthropic API shape** — the `/v1/models` endpoint returns a
   different JSON structure than OpenAI-compatible providers. Needs a
   dedicated parser. The model list is small enough that a hardcoded
   family-to-tier mapping may be more reliable than price-based ranking.

## What exists today

- `factory/scripts/openrouter-discover` — OpenRouter-only, Pi-only.
  `--list`, `--suggest`, `--check`. Public catalog endpoint, no auth
  required. 270 lines, stdlib only.
- `factory/scripts/resolve-model` — offline tier-to-model resolution
  from `model.conf`. Consumed by `trigger` and Pi's `run_agent` tool.
- `factory/scripts/matrix-lint` — validates `model.conf` syntax. Its
  `parse_matrix()` is reused by `resolve-model` and
  `openrouter-discover`.
- `config/model.conf` — the file this proposal helps populate. Now
  generated by init-factory with `CONFIGURE-ME` placeholders for
  installed CLIs only.
- VIRGIL fitting step 0 — walks the user through model.conf
  configuration. Currently manual; this proposal adds automated
  suggestions.
