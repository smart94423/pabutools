"""
Welfare-maximizing rules.
"""
from collections.abc import Iterable

import mip
from mip import Model, xsum, maximize, BINARY

from pabutools.election import (
    Instance,
    Profile,
    SatisfactionMeasure,
    SatisfactionProfile,
    Project,
    total_cost,
    MultiProfile,
    GroupSatisfactionMeasure,
    AbstractProfile,
)


def max_additive_utilitarian_welfare_scheme(
    instance: Instance,
    sat_profile: SatisfactionProfile,
    initial_budget_allocation: Iterable[Project],
    resoluteness: bool = True,
) -> Iterable[Project] | Iterable[Iterable[Project]]:
    """
    The inner algorithm for the welfare maximizing rule. It generates the corresponding budget allocations using a
    linear program solver. Note that there is no control over the way ties are broken.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        sat_profile : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
            The profile of satisfaction functions.
        initial_budget_allocation : Iterable[:py:class:`~pabutools.election.instance.Project`]
            An initial budget allocation, typically empty.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
    Returns
    -------
        Iterable[Project] | Iterable[Iterable[Project]]
            The selected projects if resolute (`resoluteness` = True), or the set of selected projects if irresolute
            (`resoluteness = False`).
    """
    score = {p: sat_profile.total_satisfaction_project(p) for p in instance}

    mip_model = Model("MaxWelfare")
    mip_model.verbose = 0
    p_vars = {
        p: mip_model.add_var(var_type=BINARY, name="x_{}".format(p))
        for p in instance
        if p not in initial_budget_allocation
    }

    mip_model.objective = maximize(xsum(p_vars[p] * score[p] for p in p_vars))

    available_budget = instance.budget_limit - total_cost(initial_budget_allocation)
    mip_model += xsum(p_vars[p] * p.cost for p in p_vars) <= available_budget

    mip_model.optimize()
    opt_value = mip_model.objective_value

    if resoluteness:
        return sorted(
            [p for p in p_vars if p_vars[p].x >= 0.99] + list(initial_budget_allocation)
        )

    previous_partial_alloc = [p for p in p_vars if p_vars[p].x >= 0.99]
    all_partial_allocs = [previous_partial_alloc]

    mip_model += xsum(p_vars[p] * score[p] for p in p_vars) == opt_value
    while True:
        # See http://yetanothermathprogrammingconsultant.blogspot.com/2011/10/integer-cuts.html
        mip_model += (
            xsum(1 - p_vars[p] for p in previous_partial_alloc)
            + xsum(p_vars[p] for p in p_vars if p not in previous_partial_alloc)
            >= 1
        )
        mip_model += (
            xsum(p_vars[p] for p in previous_partial_alloc)
            - xsum(p_vars[p] for p in p_vars if p not in previous_partial_alloc)
            <= len(previous_partial_alloc) - 1
        )

        opt_status = mip_model.optimize()
        if opt_status != mip.OptimizationStatus.OPTIMAL:
            break

        previous_partial_alloc = [p for p in p_vars if p_vars[p].x >= 0.99]
        if previous_partial_alloc not in all_partial_allocs:
            all_partial_allocs.append(previous_partial_alloc)
    return [
        sorted(partial_alloc + list(initial_budget_allocation))
        for partial_alloc in all_partial_allocs
    ]


def max_additive_utilitarian_welfare(
    instance: Instance,
    profile: AbstractProfile,
    sat_class: type[SatisfactionMeasure] = None,
    sat_profile: GroupSatisfactionMeasure = None,
    resoluteness: bool = True,
    initial_budget_allocation: Iterable[Project] = None,
) -> Iterable[Project] | Iterable[Iterable[Project]]:
    """
    Rule returning the budget allocation(s) maximizing the utilitarian social welfare. The utilitarian social welfare is
    defined as the sum of the satisfactin of the voters, where the satisfaction is computed using the satisfaction
    measure given as a parameter. The satisfaction measure is assumed to be additive. The bugdet allocation(s) are
    computed using a linear program solver. Note that there is no control over the way ties are broken.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            The class defining the satisfaction function used to measure the social welfare. It should be a class
            inhereting from pabutools.instance.satisfaction.Satisfaction.
            If no satisfaction is provided, a satisfaction profile needs to be provided. If a satisfation profile is
            provided, the satisfaction argument is disregarded.
        sat_profile : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
            The satisfaction profile corresponding to the instance and the profile. If no satisfaction profile is
            provided, but a satisfaction function is, the former is computed from the latter.
        initial_budget_allocation : Iterable[:py:class:`~pabutools.election.instance.Project`]
            An initial budget allocation, typically empty.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.

    Returns
    -------
        Iterable[Project] | Iterable[Iterable[Project]]
            The selected projects if resolute (`resoluteness` = True), or the set of selected projects if irresolute
            (`resoluteness = False`).
    """
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []

    if sat_class is None:
        if sat_profile is None:
            raise ValueError("Satisfaction and sat_profile cannot both be None.")
    else:
        if sat_profile is None:
            sat_profile = profile.as_sat_profile(sat_class=sat_class)
    return max_additive_utilitarian_welfare_scheme(
        instance, sat_profile, budget_allocation, resoluteness=resoluteness
    )
