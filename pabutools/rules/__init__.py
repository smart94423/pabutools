"""
Module introducing known rules for computing the outcome of participatory budgeting elections.

The rules implemented as:

* The utilitarian welfare maximiser: :py:func:`~pabutools.rules.maxwelfare.max_additive_utilitarian_welfare`
* The greedy approximation of the utilitarian welfare maximiser: :py:func:`~pabutools.rules.greedywelfare.greedy_utilitarian_welfare`
* The method of equal shares: :py:func:`~pabutools.rules.mes.method_of_equal_shares`
* The sequential Phragmén rule: :py:func:`~pabutools.rules.phragmen.sequential_phragmen`

Given that some rules may not used up the budget as much as possible (notably the method of equal shares and the
sequential Phragmén rule), we also implement methods to make the outcome exhaustive. Specifically, we implemented:

* The completion method by rule combination: :py:func:`~pabutools.rules.exhaustion.completion_by_rule_combination`
* The exhaustion method by budget increase: :py:func:`~pabutools.rules.exhaustion.exhaustion_by_budget_increase`
"""
from pabutools.rules.exhaustion import (
    completion_by_rule_combination,
    exhaustion_by_budget_increase,
)
from pabutools.rules.greedywelfare import greedy_utilitarian_welfare
from pabutools.rules.maxwelfare import max_additive_utilitarian_welfare
from pabutools.rules.mes import method_of_equal_shares
from pabutools.rules.phragmen import sequential_phragmen
from pabutools.rules.composition import social_welfare_comparison, popularity_comparison

__all__ = [
    "completion_by_rule_combination",
    "exhaustion_by_budget_increase",
    "greedy_utilitarian_welfare",
    "max_additive_utilitarian_welfare",
    "method_of_equal_shares",
    "sequential_phragmen",
    "social_welfare_comparison",
    "popularity_comparison",
]
