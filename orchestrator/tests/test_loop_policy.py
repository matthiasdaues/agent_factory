"""Tests for LoopPolicy."""

from __future__ import annotations

from orchestrator.loop_policy import LoopPolicy
from orchestrator.ports import FindingsStore


class StubFindingsStore:
    def __init__(self, open_counts: dict[tuple[str, int], int] | None = None) -> None:
        self.open_counts = open_counts or {}
        self.supersede_calls: list[tuple[str, int]] = []

    def ingest(self, findings) -> None:
        return None

    def supersede_prior(self, phase: str, current_iteration: int) -> int:
        self.supersede_calls.append((phase, current_iteration))
        return 7

    def open_count(self, phase: str, iteration: int) -> int:
        return self.open_counts.get((phase, iteration), 0)

    def list_open(self, phase: str, iteration: int):
        return []

    def next_id(self) -> str:
        return "FND-0001"


def test_stub_satisfies_port() -> None:
    assert isinstance(StubFindingsStore(), FindingsStore)


class TestLoopPolicy:
    def test_loop_continues_when_iteration_below_cap(self) -> None:
        policy = LoopPolicy(cap=3)
        assert policy.should_loop(2) is True

    def test_cap_reached_returns_false(self) -> None:
        policy = LoopPolicy(cap=3)
        assert policy.should_loop(3) is False

    def test_cap_zero_rejected(self) -> None:
        """FAGAN-0027: VR-002 requires cap >= 1."""
        import pytest

        with pytest.raises(ValueError, match="cap must be >= 1"):
            LoopPolicy(cap=0)

    def test_negative_cap_rejected(self) -> None:
        import pytest

        with pytest.raises(ValueError, match="cap must be >= 1"):
            LoopPolicy(cap=-1)

    def test_zero_findings_exits(self) -> None:
        store = StubFindingsStore({("phase-a", 2): 0})
        policy = LoopPolicy()
        assert policy.should_exit(store, "phase-a", 2) is True

    def test_nonzero_findings_does_not_exit(self) -> None:
        store = StubFindingsStore({("phase-a", 2): 1})
        policy = LoopPolicy()
        assert policy.should_exit(store, "phase-a", 2) is False

    def test_supersede_delegates_to_store(self) -> None:
        store = StubFindingsStore()
        policy = LoopPolicy()
        assert policy.supersede_prior(store, "phase-a", 2) == 7
        assert store.supersede_calls == [("phase-a", 2)]
