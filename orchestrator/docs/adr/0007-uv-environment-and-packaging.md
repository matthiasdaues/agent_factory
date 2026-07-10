# 0007. uv for environment, packaging, and distribution

**Status**: Accepted

## Context

The architecture documented *what* runs (chapter 7) but not *how* a person gets from a pristine machine to a running `orchestrate`. Reproducibility of the environment supports determinism (Q1) and operability (Q4): the same pinned interpreter and dependencies should behave identically on every machine. The tool also drives **other** repositories, so it must be installable as a command available outside its own source tree.

A pristine-laptop bootstrap has three tiers:

- **Tier A — system**: `git`; an authenticated AI CLI (Copilot); `Docker` (only for the architecture phase's Structurizr export). These are OS/Node/OAuth concerns; no Python tool can provide them.
- **Tier B — Python**: Python 3.10+, a virtualenv, the orchestrator + its runtime dependency `jsonschema`, and the gate/dev tools (`pre-commit`, `ruff`, `pytest`), plus a lockfile.
- **Tier C — config**: the target repo is a git repo with `.pre-commit-config.yaml` and `pre-commit install` run.

This decision concerns **Tier B** (and the distribution of the tool). It is **complementary to [ADR-0006](0006-stdlib-first-dependency-policy.md), not a revision of it**: ADR-0006 governs the *runtime* dependency surface (stdlib + `jsonschema`); this ADR governs the *build/dev/distribution* tooling. A packaging tool is not a runtime import, exactly as a compiler is not.

### Alternatives (Pugh Matrix)

Baseline **A**: `pip` + `venv` + `requirements.txt`. **B**: `uv`. **C**: Poetry. **D**: `pipx` (tool install only).

| Criterion                                | Weight | A: pip + venv | B: uv  | C: Poetry | D: pipx |
| ---------------------------------------- | ------ | ------------- | ------ | --------- | ------- |
| Reproducible environment (Q1)            | 3      | 0             | +1     | +1        | 0       |
| Pristine-laptop bootstrap effort (Q4)    | 2      | 0             | +1     | 0         | 0       |
| Manages the Python version itself (Q5)   | 2      | 0             | +1     | -1        | -1      |
| Install / resolve speed (Q4)             | 1      | 0             | +1     | -1        | 0       |
| Ecosystem maturity / single-vendor risk  | 1      | 0             | -1     | 0         | 0       |
| Minimal *added* system prerequisite (Q7) | 1      | 0             | -1     | -1        | -1      |
| **Weighted total**                       |        | **0**         | **+6** | **-1**    | **-3**  |

uv wins clearly. Its debits are youth / single-vendor (Astral) and being one extra thing to install — both minor against the reproducibility and Python-management wins. Poetry locks well but cannot install the interpreter; pipx only installs tools and manages nothing else.

## Decision

Use **uv** as the environment, packaging, and distribution tool:

- **Project definition** in `pyproject.toml`; the resolved environment pinned in **`uv.lock`** (committed) for reproducibility.
- **Runtime dependency**: `jsonschema` only (per ADR-0006). **Dev-group** dependencies (`pre-commit`, `ruff`, `pytest`) are declared in a dependency group so uv provides them for the gate and tests **without** adding to the runtime import surface.
- **Interpreter**: `uv python install` manages Python 3.10+, so "install Python" leaves the pristine-laptop list.
- **Distribution**: the tool exposes an `orchestrate` console entry point installable via **`uv tool install`**, so it runs inside any **target** repository it drives — not only its own source tree. Project-local `uv run orchestrate …` remains available for development.
- **Tier A stays manual**: uv does not install `git`, `Docker`, or the AI CLI / its auth. These remain documented prerequisites (chapter 7); no `doctor` command is introduced in this version.

## Consequences

**Positive**

- The Python side of the bootstrap collapses to `uv sync` (dev) or `uv tool install` (use); the interpreter, venv, deps, and lockfile are one tool's concern (Q4).
- `uv.lock` makes the environment reproducible across machines, reinforcing determinism of behaviour (Q1).
- ADR-0006's runtime minimalism is preserved: gate/dev tools live in a dev group, invisible to the shipped runtime.
- Installable as a global command, matching how the orchestrator is used — inside the repos it drives.

**Negative / risks**

- Adds `uv` as a required build/dev prerequisite (one install step); accepted as lighter than manual pyenv + venv + pip.
- Ties the toolchain to Astral's uv (single vendor, younger ecosystem); mitigated because `pyproject.toml` is standard and a fallback to `pip`/`venv` remains possible if ever needed.
- Tier A prerequisites are still manual and can fail a run late; mitigated only by documentation here (a preflight `doctor` command was considered and deferred — see chapter 7 / chapter 11).
