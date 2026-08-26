# FAGAN-0029 — Commit Message Format Inconsistency

**Date:** 2026-08-26  
**Severity:** Trivial  
**Category:** Consistency  
**Status:** Improvement opportunity

---

## Summary

Commit messages in `feature/mechanize-dispatch` use conventional format (`feat:`, `fix:`, `merge:`) but some documentation updates may not consistently follow the conventional prefix pattern.

## Evidence

From `git log feature/mechanize-dispatch --oneline`:
- `6431c8c feat: document tier rubric and story guidance (ST-0138)`
- `38f5145 merge: story/ST-0138 — convention docs update (ST-0138)`
- Other commits follow `feat:`, `fix:`, `chore:`, `docs:`, `merge:` patterns

## Specification Alignment

The commit convention is documented in `factory/rulebooks/conventions/commit-conventions.md` but not enforced by the CI/CD pipeline.

## Improvement Opportunity

Add a pre-commit hook or CI check to enforce conventional commit messages. This would be a minor improvement for automated changelog generation and git history analysis.

## Recommendation

Low priority. The inconsistency is cosmetic and doesn't affect functionality. Consider adding a pre-commit hook if the team values strict conventional commit enforcement.