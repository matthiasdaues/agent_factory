"""Loop policy for iteration control and finding supersession."""

from __future__ import annotations

from .ports import FindingsStore


class LoopPolicy:
    """Owns the loop cap, supersession step, and exit predicate."""

    def __init__(self, cap: int = 3) -> None:
        if cap < 1:
            raise ValueError(f"iteration cap must be >= 1, got {cap} (VR-002)")
        self.cap = cap

    def should_loop(self, iteration: int) -> bool:
        return iteration < self.cap

    def supersede_prior(self, store: FindingsStore, phase: str, iteration: int) -> int:
        return store.supersede_prior(phase, iteration)

    def should_exit(self, store: FindingsStore, phase: str, iteration: int) -> bool:
        return store.open_count(phase, iteration) == 0
