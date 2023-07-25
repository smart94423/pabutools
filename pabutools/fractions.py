"""
Module introducing all the functions used to handle fractions.
"""
from numbers import Number

from gmpy2 import mpq


FRACTION = "gmpy2"
"""
Constant describing which module to use for computing fractions. It can either be "gmpy2" or "float". The default is 
"gmpy2".
"""


def frac(*arg: Number) -> Number:
    """
    Returns a fraction instantiated from the module defined by the `FRACTION` constant. If more than two numbers are
    provided, an error is raised.

    Parameters
    ----------
        Number
            One or two numbers.

    Returns
    -------
        Number
            The fraction.
    """
    if len(arg) == 1:
        if FRACTION == "gmpy2":
            return mpq(arg[0])
        elif FRACTION == "float":
            return arg[0]
        else:
            raise ValueError(
                "The current value of pabutools.fractions.FRACTION '{}' is invalid, it needs to be in "
                "[gmpy2, float].".format(FRACTION)
            )
    elif len(arg) == 2:
        if FRACTION == "gmpy2":
            return mpq(arg[0], arg[1])
        elif FRACTION == "float":
            return arg[0] / arg[1]
        else:
            raise ValueError(
                "The current value of pabutools.fractions.FRACTION '{}' is invalid, it needs to be in "
                "[gmpy2, float].".format(FRACTION)
            )
    raise ValueError("frac can only take 1 or 2 arguments")


def str_as_frac(s: str) -> Number:
    """
    Converts a string to a fraction instantiated from the module defined by the `FRACTION` constant.

    Parameters
    ----------
        s: str
            A string representing a number.

    Returns
    -------
        Number
            The fraction.
    """
    if FRACTION == "gmpy2":
        return mpq(s)
    elif FRACTION == "float":
        return float(s)
