---
title: Conventional Commits
category: implementation
enforcement: git-hooks (optional)
version: 1.0.0
---

# Conventional Commits

Follow **Conventional Commits 1.0.0** (conventionalcommits.org): `<type>: <description>`

## Project-Specific Rule

### Story/Bug ID Required

Canonical statement: [rules.md § Commits](../rules.md#commits).

Skeleton: [commit-message.md template](../templates/commit-message.md).

### ID Formats

| Context             | ID Format    | Example                                          |
| ------------------- | ------------ | ------------------------------------------------ |
| User Story          | `ST-NNNN`    | `feat: add JWT refresh (ST-0042)`                |
| Bug Fix             | `BUG-NNNN`   | `fix: prevent null pointer (BUG-0003)`           |
| Spec Update         | `SPEC-NNNN`  | `docs: clarify use case UC-05 (SPEC-012)`        |
| Architecture Issue  | `ATAM-NNNN`  | `refactor: split service layer (ATAM-07)`        |
| Fagan Finding       | `FAGAN-NNN`  | `refactor: reduce cyclomatic (FAGAN-023)`        |
| Security Finding    | `SEC-NNNN`   | `fix: sanitize SQL input (SEC-0008)`             |
| Spec Reconciliation | `RECON-NNNN` | `docs: sync entity model with code (RECON-0004)` |

### Commit Types

Standard types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Version bumps** (see [versioning-policy.md](versioning-policy.md)):

- `feat:` → MINOR
- `fix:` → PATCH
- `BREAKING CHANGE` footer → MAJOR

## Examples

**Correct:**

```
feat: implement JWT token refresh (ST-0042)

fix: prevent race condition in orders (BUG-0018)

docs: update caching decision ADR (ATAM-0009)
```

**Incorrect:**

```
feat: add authentication
# Missing story ID

Added user login (ST-0042)
# Missing type prefix, past tense

fix: bug fix
# Vague, missing bug ID
```

## Enforcement

**Optional git hook:** `commit-msg` validates type and ID pattern.

## References

- [Conventional Commits 1.0.0](https://www.conventionalcommits.org/)
- [versioning-policy.md](versioning-policy.md)

## Referenced from

- [rules.md § Commits](../rules.md#commits)
- [architecture-agent.md § Workflow](../../agents/architecture-agent.md#workflow)
- [developer-agent.md § Workflow](../../agents/developer-agent.md#workflow)
- [requirements-agent.md § Workflow](../../agents/requirements-agent.md#workflow)
- [reconciliation-agent.md § Workflow](../../agents/reconciliation-agent.md#workflow)
- [qa-agent.md § Workflow](../../agents/qa-agent.md#workflow)
- [bug-hunt § Phase: Fix](../../skills/bug-hunt/SKILL.md#phase-fix)
- [implement-issue § Step 4 — Commit](../../skills/implement-issue/SKILL.md#step-4-commit)
- [commit](../../skills/commit/SKILL.md)
- [branching-policy.md § Commits On Feature Branches](branching-policy.md#commits-on-feature-branches)
- [versioning-policy.md § Version Bump Triggers](versioning-policy.md#version-bump-triggers)
