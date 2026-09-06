from src.module import simple_add


def test_simple_add_positive():
    assert simple_add(2, 3) == 5


def test_simple_add_negative_clamps():
    assert simple_add(-5, 10) == 10
