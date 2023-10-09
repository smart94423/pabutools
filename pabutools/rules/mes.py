"""
The method of equal shares.
"""
from copy import copy, deepcopy
from collections.abc import Iterable
from numbers import Number

from pabutools.election.satisfaction.satisfactionmeasure import GroupSatisfactionMeasure
from pabutools.election.ballot.ballot import AbstractBallot
from pabutools.election.instance import Instance, Project
from pabutools.election.profile import AbstractProfile
from pabutools.election.satisfaction import SatisfactionMeasure
from pabutools.tiebreaking import lexico_tie_breaking
from pabutools.fractions import frac
from pabutools.tiebreaking import TieBreakingRule
from pabutools.rules.exhaustion import exhaustion_by_budget_increase
from pabutools.rules.exhaustion import completion_by_rule_combination
from pabutools.rules.composition import popularity_comparison
from pabutools.rules.greedywelfare import greedy_utilitarian_welfare


class MESVoter:
    """
    Class used to summarise a voter during a run of the method of equal shares.

    Parameters
    ----------
        ballot: :py:class:`~pabutools.election.ballot.approvalballot.AbstractApprovalBallot`
            The ballot of the voter.
        sat: SatisfactionMeasure
            The satisfaction measure corresponding to the ballot.
        budget: Number
            The budget of the voter.
        multiplicity: int
            The multiplicity of the ballot.

    Attributes
    ----------
        ballot: :py:class:`~pabutools.election.ballot.approvalballot.AbstractApprovalBallot`
            The ballot of the voter.
        sat: SatisfactionMeasure
            The satisfaction measure corresponding to the ballot.
        budget: Number
            The budget of the voter.
        multiplicity: int
            The multiplicity of the ballot.
    """

    def __init__(
        self,
        ballot: AbstractBallot,
        sat: SatisfactionMeasure,
        budget: Number,
        multiplicity: int,
    ):
        self.ballot = ballot
        self.sat = sat
        self.budget = budget
        self.multiplicity = multiplicity

    def total_sat(self, projs: Iterable[Project]) -> Number:
        """
        Returns the total satisfaction given a subset of projects. It is equal to the satisfaction for the projects,
        multiplied by the multiplicity.

        Parameters
        ----------
            projs: Iterable[:py:class:`~pabutools.election.instance.Project`]
                The collection of projects.

        Returns
        -------
            Number
                The total satisfaction.
        """
        return self.multiplicity * self.sat.sat(projs)

    def total_budget(self) -> Number:
        """
        Returns the total budget of the voters. It is equal to the budget multiplied by the multiplicity.

        Returns
        -------
            Number
                The total budget.
        """
        return self.multiplicity * self.budget

    def budget_over_sat(self, projs):
        """
        Returns the budget divided by the satisfaction for a given subset of projects.

        Parameters
        ----------
            projs: Iterable[:py:class:`~pabutools.election.instance.Project`]
                The collection of projects.

        Returns
        -------
            Number
                The total satisfaction.
        """
        return frac(self.budget, self.sat.sat(projs))


def mes_scheme(
    instance: Instance,
    profile: AbstractProfile,
    sat_profile: GroupSatisfactionMeasure,
    initial_budget: Number,
    initial_budget_allocation: Iterable[Project],
    tie_breaking: TieBreakingRule,
    resoluteness=True,
) -> list[Project] | list[list[Project]]:
    """
    The inner algorithm used to compute the outcome of the Method of Equal Shares (MES). See the website
    `equalshares.net <https://equalshares.net/>`_ for details about how to compute the outcome of the rule.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        sat_profile : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
            The profile of satisfaction functions.
        initial_budget: Number
            The initial budget of a voter.
        initial_budget_allocation : Iterable[:py:class:`~pabutools.election.instance.Project`]
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
        if proj.cost == 0:
            initial_projects.remove(proj)
            if score > 0:
                initial_budget_allocation.append(proj)

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
    profile: AbstractProfile,
    sat_class: type[SatisfactionMeasure] = None,
    sat_profile: GroupSatisfactionMeasure = None,
    tie_breaking: TieBreakingRule = None,
    resoluteness: bool = True,
    initial_budget_allocation: Iterable[Project] = None,
) -> Iterable[Project] | Iterable[Iterable[Project]]:
    """
    The Method of Equal Shares (MES). See the website
    `equalshares.net <https://equalshares.net/>`_ for details about how to compute the outcome of the rule. Note that
    the satisfaction measure is asssumed to be additive.

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
            raise ValueError("sat_class and sat_profile cannot both be None")
    else:
        if sat_profile is None:
            sat_profile = profile.as_sat_profile(sat_class=sat_class)

    return mes_scheme(
        instance,
        profile,
        sat_profile,
        frac(instance.budget_limit, profile.num_ballots()),
        budget_allocation,
        tie_breaking,
        resoluteness=resoluteness,
    )


def mes_iterated(
    instance: Instance,
    profile: AbstractProfile,
    sat_class: type[SatisfactionMeasure] = None,
    sat_profile: GroupSatisfactionMeasure = None,
    initial_budget_allocation: Iterable[Project] = None,
    resoluteness: bool = True,
    budget_step: Number = None,
) -> Iterable[Project]:
    """
    Shortcut for the method of equal shares used with the exhaustion by budget increase method.

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
        budget_step: Number
            The budget increase in each step. Defaults to 1% of the budget limit.

    Returns
    -------
        Iterable[Project]
            The selected projects.
    """
    return exhaustion_by_budget_increase(
        instance,
        profile,
        method_of_equal_shares,
        {"sat_class": sat_class, "sat_profile": sat_profile},
        initial_budget_allocation=initial_budget_allocation,
        resoluteness=resoluteness,
        budget_step=budget_step,
    )


def mes_iterated_completed(
    instance: Instance,
    profile: AbstractProfile,
    sat_class: type[SatisfactionMeasure] = None,
    sat_profile: GroupSatisfactionMeasure = None,
    initial_budget_allocation: Iterable[Project] = None,
    resoluteness: bool = True,
    budget_step: Number = None,
) -> Iterable[Project]:
    """
    Shortcut for the method of equal shares used with the exhaustion by budget increase method and then complete by the
    greedy utilitarian welfare maximiser.

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
        budget_step: Number
            The budget increase in each step for the iterated MES part. Defaults to 1% of the budget limit.

    Returns
    -------
        Iterable[Project]
            The selected projects.
    """
    return completion_by_rule_combination(
        instance,
        profile,
        [mes_iterated, greedy_utilitarian_welfare],
        [
            {
                "sat_class": sat_class,
                "sat_profile": sat_profile,
                "budget_step": budget_step,
            },
            {"sat_class": sat_class, "sat_profile": sat_profile},
        ],
        initial_budget_allocation=initial_budget_allocation,
        resoluteness=resoluteness,
    )
