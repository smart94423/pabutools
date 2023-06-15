from collections.abc import Iterable

import mip
from mip import Model, xsum, maximize, BINARY

from pbvoting.instance import PBInstance, Profile, Satisfaction, SatisfactionProfile, Project


def max_welfare_scheme(instance: PBInstance,
                       sat_profile: SatisfactionProfile,
                       initial_budget_allocation: Iterable[Project],
                       resoluteness: bool = True) -> Iterable[Project] | Iterable[Iterable[Project]]:

    score = {p: sum(sat.sat([p]) for sat in sat_profile) for p in instance}

    mip_model = Model("MaxWelfare")
    p_vars = {p: mip_model.add_var(var_type=BINARY, name="x_{}".format(p))
              for p in instance if p not in initial_budget_allocation}

    mip_model.objective = maximize(xsum(p_vars[p] * score[p] for p in p_vars))

    mip_model += xsum(p_vars[p] * p.cost for p in p_vars) <= instance.budget_limit

    mip_model.optimize()
    opt_value = mip_model.objective_value

    if resoluteness:
        return sorted([p for p in instance if p_vars[p].x >= 0.99] + list(initial_budget_allocation))

    previous_partial_alloc = [p for p in instance if p_vars[p].x >= 0.99]
    all_partial_allocs = [previous_partial_alloc]

    mip_model += xsum(p_vars[p] * score[p] for p in p_vars) == opt_value
    while True:
        mip_model += xsum(p_vars[p] for p in previous_partial_alloc) <= len(previous_partial_alloc) - 1

        opt_status = mip_model.optimize()
        if opt_status != mip.OptimizationStatus.OPTIMAL:
            break

        previous_partial_alloc = [p for p in instance if p_vars[p].x >= 0.99]
        all_partial_allocs.append(previous_partial_alloc)
    return [sorted(partial_alloc) + list(initial_budget_allocation) for partial_alloc in all_partial_allocs]


def max_welfare(instance: PBInstance,
                profile: Profile,
                sat_class: type[Satisfaction] = None,
                sat_profile: SatisfactionProfile = None,
                resoluteness: bool = True,
                initial_budget_allocation: Iterable[Project] = None
                ) -> Iterable[Project] | Iterable[Iterable[Project]]:
    """
        Welfare maximiser.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.ApprovalProfile
                The profile.
            sat_class : class
                The class defining the satisfaction function used to measure the social welfare. It should be a class
                inhereting from pbvoting.instance.satisfaction.Satisfaction.
                If no satisfaction is provided, a satisfaction profile needs to be provided. If a satisfation profile is
                provided, the satisfaction argument is disregarded.
            sat_profile : pbvoting.instance.satisfaction.SatisfactionFunction
                The satisfaction profile corresponding to the instance and the profile. If no satisfaction profile is
                provided, but a satisfaction function is, the former is computed from the latter.
            resoluteness : bool, optional
                Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
                Defaults to True.
            initial_budget_allocation : collection of pbvoting.instance.pbinstance.Project, optional
                A potential initial budget allocation.
        Returns
        -------
            set of pbvoting.instance.pbinstance.Project
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
            sat_profile = SatisfactionProfile(instance=instance, profile=profile, sat_class=sat_class)

    return max_welfare_scheme(instance, sat_profile, budget_allocation, resoluteness=resoluteness)
