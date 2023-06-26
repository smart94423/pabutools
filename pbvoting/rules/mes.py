from copy import copy, deepcopy
from collections.abc import Iterable
from fractions import Fraction
from pbvoting.election.instance import Instance, Project
from pbvoting.election.profile import Profile
from pbvoting.election.satisfaction import Satisfaction, SatisfactionProfile
from pbvoting.tiebreaking import lexico_tie_breaking
from pbvoting.fractions import frac
from pbvoting.tiebreaking import TieBreakingRule


def mes_scheme(instance: Instance,
               profile: Profile,
               sat_profile: SatisfactionProfile,
               initial_budget: Fraction,
               budget_allocation: Iterable[Project],
               tie_breaking: TieBreakingRule,
               resoluteness=True
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
            budget_allocation : collection of pbvoting.instance.pbinstance.Project
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

    def aux(inst, prof, sats, tie, projects, budgets, alloc, total_scores, supporters, prev_affordability,
            all_allocs, resolute):
        tied_projects = []
        best_afford = float('inf')
        for project in sorted(projects, key=lambda p: prev_affordability[p]):
            if prev_affordability[project] > best_afford:  # best possible afford for this round isn't good enough
                break
            if sum(budgets[i] for i in supporters[project]) < project.cost:  # unaffordable, can delete
                projects.remove(project)
                continue
            supporters[project].sort(key=lambda i: budgets[i] / sats[i].sat([project]))
            paid_so_far = 0
            denominator = total_scores[project]
            for j in range(len(supporters[project])):
                rho = frac(project.cost - paid_so_far, denominator)
                if rho * sats[supporters[project][j]].sat([project]) <= budgets[supporters[project][j]]:
                    # found the best rho for this candidate
                    prev_affordability[project] = rho
                    if rho < best_afford:
                        best_afford = rho
                        tied_projects = [project]
                    elif rho == best_afford:
                        tied_projects.append(project)
                    break
                paid_so_far += budgets[supporters[project][j]]
                denominator -= sats[supporters[project][j]].sat([project])
        if not tied_projects:
            alloc.sort()
            if alloc not in all_allocs:
                all_allocs.append(alloc)
        else:
            tied_projects = tie.order(inst, prof, tied_projects)
            if resolute:
                tied_projects = tied_projects[:1]
            for selected_project in tied_projects:
                new_alloc = copy(alloc)
                new_alloc.append(selected_project)
                new_projects = copy(projects)
                new_projects.remove(selected_project)
                new_budgets = deepcopy(budgets)
                for i in supporters[selected_project]:
                    new_budgets[i] -= min(budgets[i], best_afford * sats[i].sat([selected_project]))
                new_afford = deepcopy(prev_affordability)
                aux(inst, prof, sats, tie, new_projects, new_budgets, new_alloc, total_scores, supporters, new_afford,
                    all_allocs, resolute)

    # Adapted from equalshares.net
    initial_projects = set(instance)
    for proj in budget_allocation:
        initial_projects.remove(proj)
    initial_budgets = {i: initial_budget for i in range(len(profile))}
    scores = {proj: sat_profile.total_satisfaction([proj]) for proj in initial_projects}
    for proj, score in scores.items():
        if score <= 0 or proj.cost == 0:
            initial_projects.remove(proj)
    supps = {proj: [i for i in range(len(profile)) if sat_profile[i].sat([proj]) > 0] for proj in initial_projects}
    initial_affordability = {proj: frac(proj.cost, scores[proj]) if scores[proj] > 0 else float('inf')
                             for proj in initial_projects}
    initial_budget_allocation = copy(budget_allocation)
    all_budget_allocations = []

    aux(instance, profile, sat_profile, tie_breaking, initial_projects, initial_budgets, initial_budget_allocation,
        scores, supps, initial_affordability, all_budget_allocations, resoluteness)

    if resoluteness:
        return all_budget_allocations[0]
    else:
        return all_budget_allocations


def method_of_equal_shares(instance: Instance,
                           profile: Profile,
                           sat_class: type[Satisfaction] = None,
                           sat_profile: SatisfactionProfile = None,
                           tie_breaking: TieBreakingRule = lexico_tie_breaking,
                           resoluteness: bool = True,
                           initial_budget_allocation: Iterable[Project] = None
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
            sat_profile = [sat_class(instance, profile, ballot) for ballot in profile]

    return mes_scheme(instance, profile, sat_profile, frac(instance.budget_limit, len(profile)), budget_allocation,
                      tie_breaking, resoluteness=resoluteness)
