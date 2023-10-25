"""
Module introducing all the functions used to handle fractions.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from gmpy2 import mpq

if TYPE_CHECKING:
    from pabutools.utils import Numeric

GMPY_FRAC = "gmpy2"
"""
Value of the `FRACTION` constant when gumpy2 fractions are to be used. 
"""

FLOAT_FRAC = "float"
"""
Value of the `FRACTION` constant when float fractions are to be used. 
"""

FRACTION = GMPY_FRAC
"""
Constant describing which module to use for computing fractions. It can either be "gmpy2" or "float". The default is 
"gmpy2".
"""


def frac(*arg: Numeric) -> Numeric:
    """
    Returns a fraction instantiated from the module defined by the `FRACTION` constant. If more than two numbers are
    provided, an error is raised.

    Parameters
    ----------
        Numeric
            One or two numbers.

    Returns
    -------
        Numeric
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


def str_as_frac(s: str) -> Numeric:
    """
    Converts a string to a fraction instantiated from the module defined by the `FRACTION` constant.

    Parameters
    ----------
        s: str
            A string representing a number.

    Returns
    -------
        Numeric
            The fraction.
    """
    if FRACTION == "gmpy2":
        return mpq(s)
    elif FRACTION == "float":
        return float(s)
    else:
        raise ValueError(f"The `FRACTION` constant has an unknown value: {FRACTION}")
