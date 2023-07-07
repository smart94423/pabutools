from copy import copy, deepcopy
from collections.abc import Iterable
from numbers import Number

from pbvoting.election import MultiProfile, SatisfactionMultiProfile
from pbvoting.election.instance import Instance, Project
from pbvoting.election.profile import Profile
from pbvoting.election.satisfaction import SatisfactionMeasure, SatisfactionProfile
from pbvoting.tiebreaking import lexico_tie_breaking
from pbvoting.fractions import frac
from pbvoting.tiebreaking import TieBreakingRule


class MESVoter:
    def __init__(self, ballot, sat, budget, multiplicity):
        self.ballot = ballot
        self.sat = sat
        self.budget = budget
        self.multiplicity = multiplicity

    def total_sat(self, projs):
        return self.multiplicity * self.sat.sat(projs)

    def total_budget(self):
        return self.multiplicity * self.budget

    def budget_over_sat(self, projs):
        return frac(self.budget, self.sat.sat(projs))


def mes_scheme(
    instance: Instance,
    profile: Profile,
    sat_profile: SatisfactionProfile | SatisfactionMultiProfile,
    initial_budget: Number,
    initial_budget_allocation: Iterable[Project],
    tie_breaking: TieBreakingRule,
    resoluteness=True,
) -> list[Project] | list[list[Project]]:
    """
    The inner algorithm to compute the outcome of the method of equal shares (MES). See equalshares.net for more
    details on this voting rule.
    Parameters
    ----------
        instance : pbvoting.instance.pbinstance.PBInstance
            The instance.
        profile : pbvoting.instance.profile.ApprovalProfile
            The profile.
        sat_profile : pbvoting.instance.pbinstance.SatisfactionProfile
            The profile of satisfaction functions.
        initial_budget : float
            The budget distributed to the agents initially.
        initial_budget_allocation : collection of pbvoting.instance.pbinstance.Project
            An initial budget allocation, typically empty.
        tie_breaking : pbvoting.rules.tiebreaking.TieBreakingRule
            The tie-breaking rule used.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
    Returns
    -------
        list of pbvoting.instance.pbinstance.Project if resolute, list of the previous if irresolute
    """

    def aux(
        inst,
        prof,
        voters,
        tie,
        projects,
        alloc,
        total_scores,
        supporters,
        prev_affordability,
        all_allocs,
        resolute,
    ):
        tied_projects = []
        best_afford = float("inf")
        for project in sorted(projects, key=lambda p: prev_affordability[p]):
            if (
                prev_affordability[project] > best_afford
            ):  # best possible afford for this round isn't good enough
                break
            if (
                sum(voters[i].total_budget() for i in supporters[project])
                < project.cost
            ):  # unaffordable, can delete
                projects.remove(project)
                continue
            supporters[project].sort(key=lambda i: voters[i].budget_over_sat([project]))
            paid_so_far = 0
            denominator = total_scores[project]
            for supporter_index in supporters[project]:
                supporter = voters[supporter_index]
                rho = frac(project.cost - paid_so_far, denominator)
                if rho * supporter.sat.sat([project]) <= supporter.budget:
                    # found the best rho for this candidate
                    prev_affordability[project] = rho
                    if rho < best_afford:
                        best_afford = rho
                        tied_projects = [project]
                    elif rho == best_afford:
                        tied_projects.append(project)
                    break
                paid_so_far += supporter.total_budget()
                denominator -= supporter.total_sat([project])
        if not tied_projects:
            alloc.sort()
            if alloc not in all_allocs:
                all_allocs.append(alloc)
        else:
            tied_projects = tie.order(inst, prof, tied_projects)
            if resolute:
                tied_projects = tied_projects[:1]
            for selected_project in tied_projects:
                if resolute:
                    new_alloc = alloc
                    new_projects = projects
                    new_voters = voters
                    new_afford = prev_affordability
                else:
                    new_alloc = copy(alloc)
                    new_projects = copy(projects)
                    new_voters = deepcopy(voters)
                    new_afford = deepcopy(prev_affordability)
                new_alloc.append(selected_project)
                new_projects.remove(selected_project)
                for supporter_index in supporters[selected_project]:
                    supporter = new_voters[supporter_index]
                    supporter.budget -= min(
                        supporter.budget,
                        best_afford * supporter.sat.sat([selected_project]),
                    )
                aux(
                    inst,
                    prof,
                    new_voters,
                    tie,
                    new_projects,
                    new_alloc,
                    total_scores,
                    supporters,
                    new_afford,
                    all_allocs,
                    resolute,
                )

    # Adapted from equalshares.net
    initial_projects = set(instance)
    for proj in initial_budget_allocation:
        initial_projects.remove(proj)
    scores = {proj: sat_profile.total_satisfaction([proj]) for proj in initial_projects}
    for proj, score in scores.items():
        if score <= 0 or proj.cost == 0:
            initial_projects.remove(proj)

    voters_details = [
        MESVoter(sat.ballot, sat, initial_budget, sat_profile.multiplicity(sat))
        for sat in sat_profile
    ]

    supps = {
        proj: [i for i, v in enumerate(voters_details) if v.sat.sat([proj]) > 0]
        for proj in initial_projects
    }
    initial_affordability = {
        proj: frac(proj.cost, scores[proj]) if scores[proj] > 0 else float("inf")
        for proj in initial_projects
    }
    initial_budget_allocation = copy(initial_budget_allocation)

    all_budget_allocations = []

    aux(
        instance,
        profile,
        voters_details,
        tie_breaking,
        initial_projects,
        initial_budget_allocation,
        scores,
        supps,
        initial_affordability,
        all_budget_allocations,
        resoluteness,
    )

    if resoluteness:
        return all_budget_allocations[0]
    else:
        return all_budget_allocations


def method_of_equal_shares(
    instance: Instance,
    profile: Profile | MultiProfile,
    sat_class: type[SatisfactionMeasure] = None,
    sat_profile: SatisfactionProfile | SatisfactionMultiProfile = None,
    tie_breaking: TieBreakingRule = lexico_tie_breaking,
    resoluteness: bool = True,
    initial_budget_allocation: Iterable[Project] = None,
) -> list[Project] | list[list[Project]]:
    """
    General greedy scheme for approval profiles. It selects projects in rounds, each time selecting a project that
    lead to the highest increase in total satisfaction divided by the cost of the project. Projects that would
    lead to a violation of the budget constraint are skipped.
    Parameters
    ----------
        instance : pbvoting.instance.pbinstance.PBInstance
            The instance.
        profile : pbvoting.instance.profile.ApprovalProfile
            The profile.
        satisfaction : class
            The class defining the satisfaction function used to measure the social welfare. It should be a class
            inhereting from pbvoting.instance.satisfaction.Satisfaction.
            If no satisfaction is provided, a satisfaction profile needs to be provided. If a satisfation profile is
            provided, the satisfaction argument is disregarded.
        sat_profile : pbvoting.instance.satisfaction.SatisfactionFunction
            The satisfaction profile corresponding to the instance and the profile. If no satisfaction profile is
            provided, but a satisfaction function is, the former is computed from the latter.
        tie_breaking : pbvoting.rules.tiebreaking.TieBreakingRule, optional
            The tie-breaking rule used.
            Defaults to lexico_tie_breaking.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
        initial_budget_allocation : collection of pbvoting.instance.pbinstance.Project, optional
            A potential initial budget allocation.
    Returns
    -------
        list of pbvoting.instance.pbinstance.Project
    """
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []
    if sat_class is None:
        if sat_profile is None:
            raise ValueError("sat_class and sat_profile cannot both be None")
    else:
        if sat_profile is None:
            sat_profile = profile.as_sat_profile(sat_class=sat_class)

    return mes_scheme(
        instance,
        profile,
        sat_profile,
        frac(instance.budget_limit, profile.total_len()),
        budget_allocation,
        tie_breaking,
        resoluteness=resoluteness,
    )
