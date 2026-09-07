# ruff: noqa — intentional high-complexity fixture for the crap-score gate
def simple_add(a, b):
    if a < 0:
        a = 0
    return a + b


def complex_untested(data):
    result = 0
    for item in data:
        if item > 100:
            if item % 2 == 0:
                result += item * 2
            elif item % 3 == 0:
                result += item * 3
            elif item % 5 == 0:
                result += item * 5
            else:
                result -= item
        elif item > 50:
            if item % 7 == 0:
                result += item
            elif item % 11 == 0:
                result += item * 11
            else:
                result -= 1
        elif item > 0:
            result += 1
        else:
            result -= 1
    if result > 1000:
        result = 1000
    return result
