"""Tiny mutation-analysis fixture with one survivor and one kill."""


def adjust_balance(balance, delta):
    """Intentionally under-specified by the fixture tests."""
    return balance + delta


def invoice_total(subtotal, surcharge):
    """Behavior the fixture tests fully observe."""
    return subtotal + surcharge
