from gmpy2 import mpq


def frac(x, y):
    return mpq(x, y)
    # return x/y


def number_as_frac(x):
    # return x
    return mpq(x)


def str_as_frac(s):
    # return float(s)
    return mpq(s)