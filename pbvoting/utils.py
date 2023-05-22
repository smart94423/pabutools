from itertools import combinations, chain


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))


def fixed_size_subsets(iterable, size):
    return combinations(iterable, size)
