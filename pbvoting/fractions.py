from gmpy2 import mpq

FRACTION = "gmpy2"


def frac(*arg):
    if len(arg) == 1:
        if FRACTION == "gmpy2":
            return mpq(arg[0])
        elif FRACTION == "float":
            return arg[0]
    elif len(arg) == 2:
        if FRACTION == "gmpy2":
            return mpq(arg[0], arg[1])
        elif FRACTION == "float":
            return arg[0]/arg[1]
    raise ValueError("frac can only take 1 or 2 arguments")


def str_as_frac(s):
    if FRACTION == "gmpy2":
        return mpq(s)
    elif FRACTION == "float":
        return float(s)
