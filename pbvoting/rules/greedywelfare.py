from copy import copy

from pbvoting.fractions import as_frac, frac
from pbvoting.instance.pbinstance import total_cost
from pbvoting.instance.satisfaction import AdditiveSatisfaction
from pbvoting.tiebreaking import lexico_tie_breaking


def greedy_scheme(instance, profile, sat_profile, budget_allocation, tie_breaking, resoluteness=True):
    """
        The inner algorithm for the greedy rule. It selects projects in rounds, each time selecting a project that
        lead to the highest increase in total score divided by the cost of the project. Projects that would lead to a
        violation of the budget constraint are skipped.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.ApprovalProfile
                The profile.
            sat_profile : pbvoting.instance.pbinstance.SatisfactionProfile
                The profile of satisfaction functions.
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

    def aux(inst, prof, sats, allocs, alloc, tie, resolute):
        current_cost = total_cost(alloc)
        feasible = set(project for project in instance if project not in alloc and
                       current_cost + project.cost <= instance.budget_limit)
        if len(feasible) == 0:
            alloc.sort()
            if alloc not in allocs:
                allocs.append(alloc)
        else:
            best_marginal_score = None
            argmax_marginal_score = []
            for project in feasible:
                new_alloc = copy(alloc) + [project]
                total_marginal_score = as_frac(0)
                for sat in sats:
                    total_marginal_score += frac(sat.sat(new_alloc) - sat.sat(alloc), project.cost)

                    if best_marginal_score is None or total_marginal_score > best_marginal_score:
                        best_marginal_score = total_marginal_score
                        argmax_marginal_score = [project]
                    elif total_marginal_score == best_marginal_score:
                        argmax_marginal_score.append(project)

            tied_projects = tie.order(inst, prof, argmax_marginal_score)
            if resolute:
                tied_projects = tied_projects[:1]
            for selected_project in tied_projects:
                new_alloc = copy(alloc) + [selected_project]
                aux(inst, prof, sats, allocs, new_alloc, tie, resolute)

    initial_budget_allocation = copy(budget_allocation)
    all_budget_allocations = []
    aux(instance, profile, sat_profile, all_budget_allocations, initial_budget_allocation, tie_breaking,
        resoluteness)
    if resoluteness:
        return all_budget_allocations[0]
    else:
        return all_budget_allocations


def greedy_scheme_additive(instance, profile, sat_profile, budget_allocation, tie_breaking,
                           resoluteness=True):
    """
        Faster version of the inner algorithm for the greedy rule, if the scores are additive and the same for all
        voters.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.ApprovalProfile
                The profile.
            sat_profile : pbvoting.instance.pbinstance.SatisfactionProfile
                The profile of satisfaction functions.
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
    projects = list(instance)
    for project in budget_allocation:
        projects.remove(project)
    ordered_projects = tie_breaking.order(instance, profile, projects)

    def satisfaction_density(proj):
        return frac(sum(sat.sat([proj]) for sat in sat_profile), proj.cost)

    ordered_projects.sort(key=satisfaction_density, reverse=True)

    selection = []
    remaining_budget = instance.budget_limit - total_cost(budget_allocation)
    for project in ordered_projects:
        if project.cost <= remaining_budget:
            selection.append(project)
            remaining_budget -= project.cost

    if resoluteness:
        return selection

    raise NotImplementedError("Non resolute version of greedy_scheme_unanimous_additive has not been implemented.")


def greedy_welfare_approval(instance, profile, satisfaction=None, sat_profile=None, tie_breaking=lexico_tie_breaking,
                            resoluteness=True, initial_budget_allocation=None):
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
            set of pbvoting.instance.pbinstance.Project
    """
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []

    if satisfaction is None:
        if sat_profile is None:
            raise ValueError("satisfaction and sat_profile cannot both be None")
    else:
        if sat_profile is None:
            sat_profile = [satisfaction(instance, profile, ballot) for ballot in profile]

    if resoluteness and satisfaction is not None and issubclass(satisfaction, AdditiveSatisfaction):
        return greedy_scheme_additive(instance, profile, sat_profile, budget_allocation, tie_breaking,
                                      resoluteness=resoluteness)

    return greedy_scheme(instance, profile, sat_profile, budget_allocation, tie_breaking, resoluteness=resoluteness)
