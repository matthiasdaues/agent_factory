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

| Context             | ID Format      | Example                                            |
| ------------------- | -------------- | -------------------------------------------------- |
| User Story          | `ST-NNNNNN`    | `feat: add JWT refresh (ST-004200)`                |
| Bug Fix             | `BUG-NNNNNN`   | `fix: prevent null pointer (BUG-000300)`           |
| Spec Update         | `SPEC-NNNNNN`  | `docs: clarify use case UC-05 (SPEC-001200)`       |
| Architecture Issue  | `ATAM-NNNNNN`  | `refactor: split service layer (ATAM-000700)`      |
| Fagan Finding       | `FAGAN-NNNNN`  | `refactor: reduce cyclomatic (FAGAN-02300)`        |
| Security Finding    | `SEC-NNNNNN`   | `fix: sanitize SQL input (SEC-000800)`             |
| Spec Reconciliation | `RECON-NNNNNN` | `docs: sync entity model with code (RECON-000400)` |

### Commit Types

Standard types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Version bumps** (see [versioning-policy.md](versioning-policy.md)):

- `feat:` → MINOR
- `fix:` → PATCH
- `BREAKING CHANGE` footer → MAJOR

## Examples

**Correct:**

```
feat: implement JWT token refresh (ST-004200)

fix: prevent race condition in orders (BUG-001800)

docs: update caching decision ADR (ATAM-000900)
```

**Incorrect:**

```
feat: add authentication
# Missing story ID

Added user login (ST-004200)
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
- [implement-issue § Step 4 — Commit](../../skills/implement-issue/SKILL.md#step-4--commit)
- [commit](../../skills/commit/SKILL.md)
- [branching-policy.md § Commits On Feature Branches](branching-policy.md#commits-on-feature-branches)
- [versioning-policy.md § Version Bump Triggers](versioning-policy.md#version-bump-triggers)
