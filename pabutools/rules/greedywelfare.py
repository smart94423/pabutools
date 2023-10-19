"""
Greedy approximations of the maximum welfare.
"""
from copy import copy
from collections.abc import Iterable
from math import inf
from numbers import Number

from pabutools.election import AbstractBallot
from pabutools.election.profile import AbstractProfile

from pabutools.fractions import frac
from pabutools.election.instance import Instance, total_cost, Project
from pabutools.election.satisfaction import (
    AdditiveSatisfaction,
    SatisfactionMeasure,
    GroupSatisfactionMeasure,
)
from pabutools.tiebreaking import lexico_tie_breaking, TieBreakingRule


def greedy_utilitarian_scheme(
    instance: Instance,
    profile: AbstractProfile,
    sat_profile: GroupSatisfactionMeasure,
    budget_allocation: Iterable[Project],
    tie_breaking: TieBreakingRule,
    resoluteness: bool = True,
    sat_bounds: dict[AbstractBallot, Number] = None,
) -> Iterable[Project] | Iterable[Iterable[Project]]:
    """
    The inner algorithm for the greedy rule. It selects projects in rounds, each time selecting a project that
    lead to the highest increase in total score divided by the cost of the project. Projects that would lead to a
    violation of the budget constraint are skipped.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        sat_profile : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
            The profile of satisfaction functions.
        budget_allocation : Iterable[:py:class:`~pabutools.election.instance.Project`]
            An initial budget allocation, typically empty.
        tie_breaking : :py:class:`pabutools.tiebreaking.TieBreakingRule`
            The tie-breaking rule used.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
    Returns
    -------
        Iterable[Project] | Iterable[Iterable[Project]]
            The selected projects if resolute (`resoluteness` = True), or the set of selected projects if irresolute
            (`resoluteness = False`).
    """

    def aux(inst, prof, feasible, sats, allocs, alloc, tie, resolute):
        if len(feasible) == 0:
            if resolute:
                allocs.append(alloc)
            else:
                alloc.sort()
                if alloc not in allocs:
                    allocs.append(alloc)
        else:
            best_marginal_score = None
            argmax_marginal_score = []
            for project in feasible:
                new_alloc = copy(alloc) + [project]
                if project.cost > 0:
                    total_marginal_score = frac(
                        sats.total_satisfaction(new_alloc)
                        - sats.total_satisfaction(alloc),
                        project.cost,
                    )
                else:
                    total_marginal_score = inf

                if (
                    best_marginal_score is None
                    or total_marginal_score > best_marginal_score
                ):
                    best_marginal_score = total_marginal_score
                    argmax_marginal_score = [project]
                elif total_marginal_score == best_marginal_score:
                    argmax_marginal_score.append(project)
            tied_projects = tie.order(inst, prof, argmax_marginal_score)
            if resolute:
                tied_projects = tied_projects[:1]
            for selected_project in tied_projects:
                new_alloc = copy(alloc) + [selected_project]
                new_cost = total_cost(new_alloc)
                new_feasible = []
                for project in feasible:
                    if (
                        project != selected_project
                        and new_cost + project.cost <= instance.budget_limit
                    ):
                        new_feasible.append(project)
                aux(inst, prof, new_feasible, sats, allocs, new_alloc, tie, resolute)

    initial_budget_allocation = copy(budget_allocation)
    initial_cost = total_cost(initial_budget_allocation)
    all_budget_allocations = []
    feasible_projects = []
    for p in instance:
        if (
            p not in initial_budget_allocation
            and initial_cost + p.cost <= instance.budget_limit
        ):
            feasible_projects.append(p)
    feasible_projects = sorted(feasible_projects)
    aux(
        instance,
        profile,
        feasible_projects,
        sat_profile,
        all_budget_allocations,
        initial_budget_allocation,
        tie_breaking,
        resoluteness,
    )
    if resoluteness:
        return all_budget_allocations[0]
    else:
        return all_budget_allocations


def greedy_utilitarian_scheme_additive(
    instance: Instance,
    profile: AbstractProfile,
    sat_profile: GroupSatisfactionMeasure,
    budget_allocation: Iterable[Project],
    tie_breaking: TieBreakingRule,
    resoluteness: bool = True,
) -> Iterable[Project] | Iterable[Iterable[Project]]:
    """
    Faster version of the inner algorithm for the greedy rule if the scores are additive.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        sat_profile : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
            The profile of satisfaction functions.
        budget_allocation : Iterable[:py:class:`~pabutools.election.instance.Project`]
            An initial budget allocation, typically empty.
        tie_breaking : :py:class:`pabutools.tiebreaking.TieBreakingRule`
            The tie-breaking rule used.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
    Returns
    -------
        Iterable[Project] | Iterable[Iterable[Project]]
            The selected projects if resolute (`resoluteness` = True), or the set of selected projects if irresolute
            (`resoluteness = False`).
    """
    if not resoluteness:
        return greedy_utilitarian_scheme(
            instance,
            profile,
            sat_profile,
            budget_allocation,
            tie_breaking,
            resoluteness,
        )

    projects = sorted(instance)
    for project in budget_allocation:
        projects.remove(project)
    projects = tie_breaking.order(instance, profile, projects)

    def satisfaction_density(proj):
        total_sat = sat_profile.total_satisfaction_project(proj)
        if total_sat > 0:
            if proj.cost > 0:
                return frac(total_sat, proj.cost)
            return inf
        return 0

    # We sort based on a tuple to ensure ties are broken as intended
    ordered_projects = sorted(
        projects, key=lambda p: (-satisfaction_density(p), projects.index(p))
    )

    selection = list(budget_allocation)
    remaining_budget = instance.budget_limit - total_cost(budget_allocation)
    for project in ordered_projects:
        if project.cost <= remaining_budget:
            selection.append(project)
            remaining_budget -= project.cost
    return selection


def greedy_utilitarian_welfare(
    instance: Instance,
    profile: AbstractProfile,
    sat_class: type[SatisfactionMeasure] = None,
    sat_profile: GroupSatisfactionMeasure = None,
    is_sat_additive: bool = None,
    tie_breaking: TieBreakingRule = None,
    resoluteness: bool = True,
    initial_budget_allocation: Iterable[Project] = None,
) -> Iterable[Project] | Iterable[Iterable[Project]]:
    """
    General greedy scheme for approximating the utilitarian welfare. It selects projects in rounds, each time selecting
    a project that lead to the highest increase in total satisfaction divided by the cost of the project. Projects that
    would lead to a violation of the budget constraint are skipped.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            The class defining the satisfaction function used to measure the social welfare. It should be a class
            inhereting from :py:class:`pabutools.instance.satisfaction.Satisfaction`.
            If no satisfaction is provided, a satisfaction profile needs to be provided. If a satisfation profile is
            provided, the satisfaction argument is disregarded.
        sat_profile : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
            The satisfaction profile corresponding to the instance and the profile. If no satisfaction profile is
            provided, but a satisfaction function is, the former is computed from the latter.
        is_sat_additive : bool
            A boolean indicating if the satisfaction function is additive. This is directly deducted if sat_class
            is provided.
        initial_budget_allocation : Iterable[:py:class:`~pabutools.election.instance.Project`]
            An initial budget allocation, typically empty.
        tie_breaking : :py:class:`pabutools.tiebreaking.TieBreakingRule`, optional
            The tie-breaking rule used.
            Defaults to the lexicographic tie-breaking.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.

    Returns
    -------
        Iterable[Project] | Iterable[Iterable[Project]]
            The selected projects if resolute (`resoluteness` = True), or the set of selected projects if irresolute
            (`resoluteness = False`).
    """
    if tie_breaking is None:
        tie_breaking = lexico_tie_breaking
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []
    if sat_class is None:
        if sat_profile is None:
            raise ValueError("sat_class and sat_profile cannot both be None.")
    else:
        if sat_profile is None:
            sat_profile = profile.as_sat_profile(sat_class)
        if is_sat_additive is None:
            is_sat_additive = issubclass(sat_class, AdditiveSatisfaction)

    if is_sat_additive:
        return greedy_utilitarian_scheme_additive(
            instance,
            profile,
            sat_profile,
            budget_allocation,
            tie_breaking,
            resoluteness=resoluteness,
        )
    return greedy_utilitarian_scheme(
        instance,
        profile,
        sat_profile,
        budget_allocation,
        tie_breaking,
        resoluteness=resoluteness,
    )
