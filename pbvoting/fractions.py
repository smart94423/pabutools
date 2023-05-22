from fractions import Fraction


def frac(x, y):
    return Fraction(x, y)


def as_frac(x):
    return Fraction(*x.as_integer_ratio())
