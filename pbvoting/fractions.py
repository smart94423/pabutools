from fractions import Fraction


def frac(x, y):
    return Fraction(x, y)


def number_as_frac(x):
    return Fraction(*x.as_integer_ratio())


def str_as_frac(s):
    return Fraction(s)