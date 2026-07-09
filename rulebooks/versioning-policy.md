---
title: Semantic Versioning
category: release
enforcement: git-hooks, CI validation
version: 1.0.0
---

# Semantic Versioning

Follow **Semantic Versioning 2.0.0** (semver.org): `MAJOR.MINOR.PATCH`

## Project-Specific Rules

### Git Tag Must Match Version File

**MUST**: Git tag and version file are identical. No mismatches.

**Version file location:**

- Node.js/TypeScript: `package.json` (`version`)
- Python: `pyproject.toml` or `__version__.py`
- Go: Git tag only
- Rust: `Cargo.toml` (`version`)

### Branch-Specific Tag Format

| Branch      | Tag Format      | Example         |
| ----------- | --------------- | --------------- |
| main/master | `vX.Y.Z`        | `v1.2.3`        |
| dev/develop | `vX.Y.Z-beta.N` | `v1.3.0-beta.1` |
|             | `vX.Y.Z-rc.N`   | `v1.3.0-rc.1`   |
| feature/\*  | **No tags**     | version: `-dev` |

**MUST NOT:**

- ❌ Tag feature branches
- ❌ Release tags (`vX.Y.Z`) on non-main branches
- ❌ Pre-release tags (`-beta`, `-rc`) on main

### Version Bump Triggers

From **Conventional Commits** (see [commit-conventions.md](commit-conventions.md)):

| Commit Type       | Bump  |
| ----------------- | ----- |
| `feat:`           | MINOR |
| `fix:`            | PATCH |
| `BREAKING CHANGE` | MAJOR |

### Breaking Changes

Declare in commit footer:

```
feat: redesign auth API (ST-0089)

BREAKING CHANGE: Session cookies removed. Migrate to JWT tokens.
```

## Enforcement

**Pre-release hook** validates:

- Tag matches version file
- Tag format matches branch (main = release, dev = beta/rc)
- Feature branches not tagged

**CI** validates:

- Version file exists, valid semver
- Tag matches version file
- Branch-tag format compliance

## Examples

**Dev branch:**

```bash
npm version 1.3.0-beta.1
git tag v1.3.0-beta.1
```

**Main branch (after dev merge):**

```bash
npm version 1.3.0
git tag v1.3.0
```

**Feature branch:**

```bash
# version file: "1.3.0-dev"
# No tags
```

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [commit-conventions.md](commit-conventions.md)
