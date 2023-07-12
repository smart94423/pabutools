from collections.abc import Iterable
from itertools import combinations, chain
from numbers import Number

import numpy as np

from pabutools.fractions import frac


def mean_generator(generator: Iterable[Number]):
    n = 0
    mean = 0
    for x in generator:
        n += 1
        mean += frac(x - mean, n)
    return mean


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def gini_coefficient(values):
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
