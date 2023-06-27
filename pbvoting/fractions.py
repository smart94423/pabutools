from gmpy2 import mpq

FRACTION = "gmpy2"


def frac(x, y):
    if FRACTION == "gmpy2":
        return mpq(x, y)
    elif FRACTION == "float":
        return x/y


def str_as_frac(s):
    if FRACTION == "gmpy2":
        return mpq(s)
    elif FRACTION == "float":
        return float(s)
