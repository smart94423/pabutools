from itertools import combinations, chain
import numpy as np


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def gini_coefficient(values):
    values = np.asarray(values)
    if np.any(values < 0):
        raise ValueError("Negative values not supported by gini coefficient implementation.")
    if np.all(values == 0):
        return 0
    n = len(values)
    sorted_values = np.sort(values)
    cum_sorted_values = np.cumsum(sorted_values)
    return (n + 1 - 2 * np.sum(cum_sorted_values) / cum_sorted_values[-1]) / n
