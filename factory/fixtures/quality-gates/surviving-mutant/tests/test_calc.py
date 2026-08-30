"""Fixture tests for the mutation-analysis quality gate."""

from calc import adjust_balance, invoice_total


def test_adjust_balance_with_zero_delta() -> None:
    """Leaves the + -> - mutant alive because delta stays neutral."""
    assert adjust_balance(10, 0) == 10


def test_invoice_total_adds_surcharge() -> None:
    """Kills the + -> - mutant on invoice_total."""
    assert invoice_total(10, 3) == 13
