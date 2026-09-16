"""Contract tests for the readiness evaluator.

Owned contracts:
  - All evidence passing marks a route as supported (standard risk)
  - One check failing marks the route as not supported (standard risk)
  - Mechanical validation runs regardless of code changes (standard risk)
  - Semantic assessment runs only when code_changed=True (standard risk)
  - Route-specific validator mapping: only declared validators apply (standard risk)
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = REPO_ROOT / "packages" / "factory"

if str(PACKAGES_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGES_DIR))

from engine.cycle_model import Route
from engine.readiness import RouteReadiness, evaluate_readiness


@dataclass(frozen=True)
class FakeCheck:
    name: str
    passed: bool
    detail: str = ""


@dataclass(frozen=True)
class FakeValidatorResult:
    artifact_type: str
    artifact_ref: str
    assessed_commit: str
    checks: tuple
    warnings: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)


def _route(
    from_cycle: str, to_cycle: str, validators: tuple[str, ...] = ("v",),
) -> Route:
    return Route(
        from_cycle=from_cycle, to_cycle=to_cycle,
        recommend_if="test evidence", validators=validators,
    )


def _passing_result() -> FakeValidatorResult:
    return FakeValidatorResult(
        artifact_type="proposal",
        artifact_ref="docs/proposals/test.md",
        assessed_commit="abc123",
        checks=(FakeCheck("check_a", True), FakeCheck("check_b", True)),
    )


def _failing_result() -> FakeValidatorResult:
    return FakeValidatorResult(
        artifact_type="proposal",
        artifact_ref="docs/proposals/test.md",
        assessed_commit="abc123",
        checks=(FakeCheck("check_a", True), FakeCheck("check_b", False, "failed")),
        warnings=("check_b failed",),
    )


class TestAllEvidencePassing:
    def test_route_marked_supported(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness("IDEA", routes, {"v": _passing_result()})
        assert len(results) == 1
        assert results[0].supported is True

    def test_multiple_validators_all_pass(self):
        routes = [_route("IDEA", "CONCEPT", validators=("v1", "v2"))]
        results = evaluate_readiness(
            "IDEA", routes,
            {"v1": _passing_result(), "v2": _passing_result()},
        )
        assert results[0].supported is True


class TestOneCheckFailing:
    def test_route_marked_not_supported(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness("IDEA", routes, {"v": _failing_result()})
        assert len(results) == 1
        assert results[0].supported is False

    def test_warnings_propagated(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness("IDEA", routes, {"v": _failing_result()})
        assert len(results[0].warnings) > 0


class TestNoValidators:
    def test_empty_validators_not_supported(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness("IDEA", routes, {})
        assert results[0].supported is False

    def test_route_with_no_declared_validators(self):
        routes = [_route("IDEA", "CONCEPT", validators=())]
        results = evaluate_readiness("IDEA", routes, {"v": _passing_result()})
        assert results[0].supported is False


class TestOnlyOutgoingRoutes:
    def test_filters_to_current_cycle(self):
        routes = [
            _route("IDEA", "CONCEPT"),
            _route("CONCEPT", "ROADMAP"),
            _route("CONCEPT", "REALIZE"),
        ]
        results = evaluate_readiness("CONCEPT", routes, {"v": _passing_result()})
        assert len(results) == 2
        assert all(r.from_cycle == "CONCEPT" for r in results)

    def test_no_outgoing_returns_empty(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness("DONE", routes, {"v": _passing_result()})
        assert len(results) == 0


class TestRouteSpecificMapping:
    def test_route_sees_only_its_validators(self):
        routes = [
            _route("CONCEPT", "ROADMAP", validators=("v1",)),
            _route("CONCEPT", "REFINE", validators=("v2",)),
        ]
        results = evaluate_readiness(
            "CONCEPT", routes,
            {"v1": _passing_result(), "v2": _failing_result()},
        )
        roadmap = next(r for r in results if r.to_cycle == "ROADMAP")
        refine = next(r for r in results if r.to_cycle == "REFINE")
        assert roadmap.supported is True
        assert refine.supported is False

    def test_route_ignores_unrelated_validators(self):
        routes = [_route("IDEA", "CONCEPT", validators=("v1",))]
        results = evaluate_readiness(
            "IDEA", routes,
            {"v1": _passing_result(), "v2": _failing_result()},
        )
        assert results[0].supported is True
        assert len(results[0].evidence) == 1


class TestMechanicalVsSemantic:
    def test_mechanical_runs_without_code_change(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness(
            "IDEA", routes, {"v": _passing_result()}, code_changed=False,
        )
        assert len(results) == 1
        assert len(results[0].evidence) > 0

    def test_mechanical_runs_with_code_change(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness(
            "IDEA", routes, {"v": _passing_result()}, code_changed=True,
        )
        assert len(results) == 1
        assert len(results[0].evidence) > 0

    def test_semantic_excluded_when_no_code_change(self):
        routes = [_route("IDEA", "CONCEPT", validators=("sem",))]
        results = evaluate_readiness(
            "IDEA", routes,
            mechanical_results={},
            semantic_results={"sem": _passing_result()},
            code_changed=False,
        )
        assert results[0].supported is False
        assert len(results[0].evidence) == 0

    def test_semantic_included_when_code_changed(self):
        routes = [_route("IDEA", "CONCEPT", validators=("sem",))]
        results = evaluate_readiness(
            "IDEA", routes,
            mechanical_results={},
            semantic_results={"sem": _passing_result()},
            code_changed=True,
        )
        assert results[0].supported is True
        assert len(results[0].evidence) == 1

    def test_both_mechanical_and_semantic_when_code_changed(self):
        routes = [_route("IDEA", "CONCEPT", validators=("mech", "sem"))]
        results = evaluate_readiness(
            "IDEA", routes,
            mechanical_results={"mech": _passing_result()},
            semantic_results={"sem": _passing_result()},
            code_changed=True,
        )
        assert results[0].supported is True
        assert len(results[0].evidence) == 2

    def test_semantic_failure_blocks_route(self):
        routes = [_route("IDEA", "CONCEPT", validators=("mech", "sem"))]
        results = evaluate_readiness(
            "IDEA", routes,
            mechanical_results={"mech": _passing_result()},
            semantic_results={"sem": _failing_result()},
            code_changed=True,
        )
        assert results[0].supported is False


class TestReadinessShape:
    def test_result_has_required_fields(self):
        routes = [_route("IDEA", "CONCEPT")]
        results = evaluate_readiness("IDEA", routes, {"v": _passing_result()})
        r = results[0]
        assert r.from_cycle == "IDEA"
        assert r.to_cycle == "CONCEPT"
        assert isinstance(r.recommend_if, str)
        assert isinstance(r.supported, bool)
        assert isinstance(r.evidence, tuple)
        assert isinstance(r.warnings, tuple)
