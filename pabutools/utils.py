"""
Collection of util functions.
"""
from collections.abc import Iterable, Generator
from itertools import combinations, chain
from numbers import Number

import numpy as np

from pabutools.fractions import frac


def mean_generator(generator: Iterable[Number] | Iterable[tuple[Number, int]]) -> Number:
    """
    Computes the mean of a sequence of numbers given as a generator. If the generator contains tuples, the first element
    is assumed to be the value and the second its multiplicity.

    Parameters
    ----------
        generator: Iterable[Number] | Iterable[tuple[Number, int]
            The generator.

    Returns
    -------
        Number
            The mean of the values.
    """
    n = 0
    mean = 0
    for x in generator:
        multiplicity = 1
        value = x
        if type(x) is tuple:
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


def gini_coefficient(values) -> Number:
    """
    Returns the Gini coefficient of the vector of values given as argument.

    Parameters
    ----------
        values
            A vector of values.

    Returns
    -------
        Number
            The Gini coefficient.

    """
    if np.any(values < 0):
        raise ValueError(
            "Negative values not supported by gini coefficient implementation."
        )
    if np.all(values == 0):
        return 0
    n = len(values)
    sorted_values = np.sort(values)
    cum_sorted_values = np.cumsum(sorted_values)
    return frac(n + 1 - frac(2 * np.sum(cum_sorted_values), cum_sorted_values[-1]), n)
