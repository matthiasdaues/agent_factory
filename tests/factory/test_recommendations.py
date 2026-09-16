"""Contract tests for the route recommender.

Owned contracts:
  - Zero supported routes → no recommendation with warnings (standard risk)
  - One supported route → recommendation with evidence (standard risk)
  - Multiple supported routes → unranked choices (standard risk)
  - Recommender never selects between multiple routes (standard risk)
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages" / "factory"

if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.readiness import RouteReadiness
from engine.recommendations import (
    MultipleChoices,
    NoRecommendation,
    SingleRecommendation,
    recommend,
)


def _verdict(from_c: str, to_c: str, supported: bool, warnings: tuple[str, ...] = ()) -> RouteReadiness:
    return RouteReadiness(
        from_cycle=from_c,
        to_cycle=to_c,
        recommend_if="test",
        supported=supported,
        evidence=(),
        warnings=warnings,
    )


class TestZeroSupportedRoutes:
    def test_returns_no_recommendation(self):
        verdicts = [
            _verdict("IDEA", "CONCEPT", False, ("proposal missing",)),
        ]
        result = recommend("IDEA", verdicts)
        assert isinstance(result, NoRecommendation)

    def test_warnings_included(self):
        verdicts = [
            _verdict("IDEA", "CONCEPT", False, ("proposal missing",)),
        ]
        result = recommend("IDEA", verdicts)
        assert "proposal missing" in result.warnings

    def test_available_cycles_listed(self):
        verdicts = [_verdict("IDEA", "CONCEPT", False)]
        result = recommend("IDEA", verdicts)
        assert len(result.available_cycles) > 0
        assert "IDEA" not in result.available_cycles

    def test_no_verdicts_returns_no_recommendation(self):
        result = recommend("IDEA", [])
        assert isinstance(result, NoRecommendation)


class TestOneSupportedRoute:
    def test_returns_single_recommendation(self):
        verdicts = [
            _verdict("IDEA", "CONCEPT", True),
        ]
        result = recommend("IDEA", verdicts)
        assert isinstance(result, SingleRecommendation)
        assert result.recommended_cycle == "CONCEPT"

    def test_evidence_included(self):
        evidence_verdict = RouteReadiness(
            from_cycle="IDEA",
            to_cycle="CONCEPT",
            recommend_if="proposal accepted",
            supported=True,
            evidence=("check_a passed", "check_b passed"),
        )
        result = recommend("IDEA", [evidence_verdict])
        assert isinstance(result, SingleRecommendation)
        assert len(result.evidence) > 0

    def test_available_cycles_listed(self):
        verdicts = [_verdict("IDEA", "CONCEPT", True)]
        result = recommend("IDEA", verdicts)
        assert isinstance(result, SingleRecommendation)
        assert "CONCEPT" not in result.available_cycles
        assert len(result.available_cycles) > 0

    def test_one_supported_one_not(self):
        verdicts = [
            _verdict("CONCEPT", "ROADMAP", True),
            _verdict("CONCEPT", "REFINE", False),
            _verdict("CONCEPT", "REALIZE", False),
        ]
        result = recommend("CONCEPT", verdicts)
        assert isinstance(result, SingleRecommendation)
        assert result.recommended_cycle == "ROADMAP"


class TestMultipleSupportedRoutes:
    def test_returns_multiple_choices(self):
        verdicts = [
            _verdict("CONCEPT", "ROADMAP", True),
            _verdict("CONCEPT", "REFINE", True),
        ]
        result = recommend("CONCEPT", verdicts)
        assert isinstance(result, MultipleChoices)

    def test_choices_are_unranked(self):
        verdicts = [
            _verdict("CONCEPT", "ROADMAP", True),
            _verdict("CONCEPT", "REFINE", True),
            _verdict("CONCEPT", "REALIZE", True),
        ]
        result = recommend("CONCEPT", verdicts)
        assert isinstance(result, MultipleChoices)
        targets = {c.to_cycle for c in result.choices}
        assert targets == {"ROADMAP", "REFINE", "REALIZE"}

    def test_engine_does_not_select(self):
        verdicts = [
            _verdict("CONCEPT", "ROADMAP", True),
            _verdict("CONCEPT", "REFINE", True),
        ]
        result = recommend("CONCEPT", verdicts)
        assert isinstance(result, MultipleChoices)
        assert not hasattr(result, "recommended_cycle") or not isinstance(result, SingleRecommendation)

    def test_available_cycles_excludes_choices(self):
        verdicts = [
            _verdict("CONCEPT", "ROADMAP", True),
            _verdict("CONCEPT", "REFINE", True),
        ]
        result = recommend("CONCEPT", verdicts)
        choice_targets = {c.to_cycle for c in result.choices}
        for c in result.available_cycles:
            assert c not in choice_targets


class TestResultShape:
    def test_no_recommendation_has_kind(self):
        result = recommend("IDEA", [])
        assert result.kind == "none"

    def test_single_has_kind(self):
        result = recommend("IDEA", [_verdict("IDEA", "CONCEPT", True)])
        assert result.kind == "single"

    def test_multiple_has_kind(self):
        verdicts = [
            _verdict("CONCEPT", "ROADMAP", True),
            _verdict("CONCEPT", "REFINE", True),
        ]
        result = recommend("CONCEPT", verdicts)
        assert result.kind == "multiple"
