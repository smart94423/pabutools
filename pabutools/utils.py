"""
Collection of util functions.
"""
from __future__ import annotations

from collections.abc import Iterable, Generator
from itertools import combinations, chain

from typing import Union

from gmpy2 import mpq

from pabutools.fractions import frac

Numeric = Union[int, float, mpq]
"""
Type for numeric values. Is the union of int, float and mpq fractions (from the gumpy2 package).
"""


def mean_generator(
    generator: Iterable[Numeric] | Iterable[tuple[Numeric, int]]
) -> Numeric:
    """
    Computes the mean of a sequence of numbers given as a generator. If the generator contains tuples, the first element
    is assumed to be the value and the second its multiplicity.

    Parameters
    ----------
        generator: Iterable[Numeric] | Iterable[tuple[Numeric, int]
            The generator.

    Returns
    -------
        Numeric
            The mean of the values.
    """
    n: int = 0
    mean: Numeric = 0
    for x in generator:
        multiplicity: int = 1
        value: Numeric = x
        if isinstance(x, tuple):
            value = x[0]
            multiplicity = x[1]
        for i in range(multiplicity):
            n += 1
            mean += frac(value - mean, n)
    return mean


def powerset(iterable: Iterable) -> Generator:
    """
    Returns a generator of all the subsets of a given iterable.

    Parameters
    ----------
        iterable: Iterable
            An iterable.

    Returns
    -------
        Generator
            A generator of all the subsets of the iterable.
    """
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def gini_coefficient(values: Iterable[Numeric]) -> Numeric:
    """
    Returns the Gini coefficient of the vector of values given as argument.

    Parameters
    ----------
        values: Iterable[Numeric]
            A vector of values.

    Returns
    -------
        Numeric
            The Gini coefficient.

    """
    all_nul: bool = True
    num_values: int = 0
    for v in values:
        if v < 0:
            raise ValueError(
                "Negative values not supported by gini coefficient implementation."
            )
        if all_nul and v > 0:
            all_nul = False
        num_values += 1
    if all_nul:
        return 0
    sorted_values: list[Numeric] = sorted(values)
    total_cum_sum: Numeric = 0
    for i, v in enumerate(sorted_values):
        total_cum_sum += v * (num_values - i)
    return frac(num_values + 1 - frac(2 * total_cum_sum, sum(values)), num_values)
