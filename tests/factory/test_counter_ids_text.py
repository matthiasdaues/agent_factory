"""Text tests for the counter-ids rules (ST-0373, counter-ids.feature)."""

from __future__ import annotations

import re

import pytest
from conftest import REPO_ROOT

RULES = REPO_ROOT / "packages/factory/rulebooks/rules.md"
BRANCHING_POLICY = REPO_ROOT / "packages/factory/rulebooks/conventions/branching-policy.md"
PLANNING_AGENT = REPO_ROOT / "packages/factory/agents/planning-agent.md"

# A sentence that tells the reader to commit indexed artifacts to dev, or to
# keep them off other branches.
DEV_ONLY = re.compile(
    r"(commit[^.\n]*(indexed artifacts|backlog stories)[^.\n]*to `dev`"
    r"|(indexed artifacts|backlog stories)[^.\n]*(are )?(always )?committed to `dev`"
    r"|never commit indexed artifacts to a feature"
    r"|`dev`[^.\n]*(single )?canonical index)",
    re.IGNORECASE,
)


def _branching_section(text: str) -> str:
    start = text.index("## Branching")
    following = re.search(r"^## ", text[start + 3 :], re.MULTILINE)
    return text[start : start + 3 + following.start()] if following else text[start:]


def _indexed_text(path) -> str:
    text = path.read_text()
    return _branching_section(text) if path == RULES else text


@pytest.mark.spec("CID-08-LN-01")
@pytest.mark.parametrize("path", [RULES, BRANCHING_POLICY, PLANNING_AGENT], ids=lambda p: p.name)
def test_st_0373_file_allows_indexed_artifacts_on_any_branch(path):
    text = _indexed_text(path)
    assert re.search(r"indexed artifacts?[^.\n]*any branch", text, re.IGNORECASE)
    assert "next-id" in text


@pytest.mark.spec("CID-08-LN-01")
@pytest.mark.parametrize("path", [RULES, BRANCHING_POLICY, PLANNING_AGENT], ids=lambda p: p.name)
def test_st_0373_file_requires_no_indexed_artifact_on_dev(path):
    assert DEV_ONLY.search(_indexed_text(path)) is None


@pytest.mark.spec("CID-08-LN-01")
def test_st_0373_branching_policy_drops_the_dev_only_heading():
    assert "Indexed Artifacts On Dev" not in BRANCHING_POLICY.read_text()
