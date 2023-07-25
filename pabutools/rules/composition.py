"""
Module implementing different ways to compose rules.
"""
from collections.abc import Iterable, Callable

from pabutools.election import (
    Instance,
    Profile,
    Project,
    SatisfactionMeasure,
)


def popularity_comparison(
    instance: Instance,
    profile: Profile,
    sat_class: type[SatisfactionMeasure],
    rule_sequence: Iterable[Callable],
    rule_params: Iterable[dict] = None,
    initial_budget_allocation: Iterable[Project] = None,
) -> Iterable[Iterable[Project]]:
    """
    Compute the outcome of several rules and returns the one that is the most preferred by the largest set of voters,
    according to a given satisfaction measure. Should only be applied to resolute rules.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        sat_class: type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            The satisfaction measure used to do the comparison.
        rule_sequence: Iterable[Callable]
            Iterable of the rule functions.
        rule_params: Iterable[dict], optional
            Iterable of dictionaries of additional parameters that are passed as keyword arguments to the rule
            functions. Defaults to `{}`.
        initial_budget_allocation: Iterable[Project], optional
            An initial budget allocation, typically empty. Defaults to `[]`.

    Returns
    -------
        Iterable[Iterable[:py:class:`~pabutools.election.instance.Project`]]
            All the budget allocations yielding the maximum total satisfaction for the outcomes of the rules.
    """
    if rule_params is not None and len(rule_sequence) != len(rule_params):
        raise ValueError(
            "Parameters rule_sequence and rule_params must be of equal length."
        )
    if rule_params is None:
        rule_params = [{} for _ in rule_sequence]
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []
    results = []
    for index, rule in enumerate(rule_sequence):
        res = rule(
            instance,
            profile,
            initial_budget_allocation=budget_allocation,
            **rule_params[index],
        )
        if res not in results:
            results.append(res)

    sat_profile = profile.as_sat_profile(sat_class)
    result_support = [0 for _ in results]
    for sat in sat_profile:
        sats = [sat.sat(r) for r in results]
        max_sat = None
        arg_max_sat = None
        for i, s in enumerate(sats):
            if max_sat is None or s > max_sat:
                max_sat = s
                arg_max_sat = [i]
            elif s == max_sat:
                arg_max_sat.append(i)
        for i in arg_max_sat:
            result_support[i] += sat_profile.multiplicity(sat)

    max_support = max(result_support)
    argmax_support = [i for i, s in enumerate(result_support) if s == max_support]
    return [results[i] for i in argmax_support]


def social_welfare_comparison(
    instance: Instance,
    profile: Profile,
    sat_class: type[SatisfactionMeasure],
    rule_sequence: Iterable[Callable],
    rule_params: Iterable[dict] = None,
    initial_budget_allocation: Iterable[Project] = None,
) -> Iterable[Iterable[Project]]:
    """
    Compute the outcome of several rules and returns the one that is the most preferred by the voters according to a
    given satisfaction measure. Should only be applied to resolute rules.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        sat_class: type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            The satisfaction measure used to do the comparison.
        rule_sequence: Iterable[Callable]
            Iterable of the rule functions.
        rule_params: Iterable[dict], optional
            Iterable of dictionaries of additional parameters that are passed as keyword arguments to the rule
            functions. Defaults to `{}`.
        initial_budget_allocation: Iterable[Project], optional
            An initial budget allocation, typically empty. Defaults to `[]`.

    Returns
    -------
        Iterable[Iterable[:py:class:`~pabutools.election.instance.Project`]]
            All the budget allocations yielding the maximum total satisfaction for the outcomes of the rules.
    """
    if rule_params is not None and len(rule_sequence) != len(rule_params):
        raise ValueError(
            "Parameters rule_sequence and rule_params must be of equal length."
        )
    if rule_params is None:
        rule_params = [{} for _ in rule_sequence]
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []
    results = []
    for index, rule in enumerate(rule_sequence):
        res = rule(
            instance,
            profile,
            initial_budget_allocation=budget_allocation,
            **rule_params[index],
        )
        if res not in results:
            results.append(res)

    sat_profile = profile.as_sat_profile(sat_class)

    max_social_welfare = None
    argmax_social_welfare = None
    for result in results:
        social_welfare = sat_profile.total_satisfaction(result)
        if max_social_welfare is None or social_welfare > max_social_welfare:
            max_social_welfare = social_welfare
            argmax_social_welfare = [result]
        elif social_welfare == max_social_welfare:
            argmax_social_welfare.append(result)
    return argmax_social_welfare
