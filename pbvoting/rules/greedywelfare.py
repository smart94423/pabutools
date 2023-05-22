from copy import copy
from fraction import Fraction

from pbvoting.instance.pbinstance import total_cost
from pbvoting.tiebreaking import LEXICO_TIE_BREAKING
from pbvoting.utils import fixed_size_subsets
from pbvoting.instance.satisfaction import AdditiveSatisfactionFunction


def greedy_scheme(instance, profile, budget_allocation, score_function, tie_breaking,
                  resoluteness=True):
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
            budget_allocation : collection of pbvoting.instance.pbinstance.Project
                An initial budget allocation, typically empty.
            score_function : func
                The score function used that maps instances, ballots and sets of projects to a score.
            tie_breaking : pbvoting.rules.tiebreaking.TieBreakingRule
                The tie-breaking rule used.
            resoluteness : bool, optional
                Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
                Defaults to True.
        Returns
        -------
            list of pbvoting.instance.pbinstance.Project if resolute, list of the previous if irresolute
    """

    def aux(inst, prof, allocs, alloc, score, tie, resolute):
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
                total_marginal_score = Fraction(0)
                for ballot in prof:
                    total_marginal_score += Fraction(score(inst, ballot, new_alloc) -
                                                     score(inst, ballot, alloc), project.cost)

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
                aux(inst, prof, allocs, new_alloc, score, tie, resolute)

    initial_budget_allocation = copy(budget_allocation)
    all_budget_allocations = []
    aux(instance, profile, all_budget_allocations, initial_budget_allocation, score_function, tie_breaking,
        resoluteness)
    if resoluteness:
        return all_budget_allocations[0]
    else:
        return all_budget_allocations


def greedy_scheme_additive_satisfaction(instance, profile, budget_allocation, score_function, tie_breaking,
                                        resoluteness=True):
    """
        Faster version of the inner algorithm for the greedy rule, if the satisfaction function is additive.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.ApprovalProfile
                The profile.
            budget_allocation : collection of pbvoting.instance.pbinstance.Project
                An initial budget allocation, typically empty.
            score_function : func
                The score function used that maps instances, ballots and sets of projects to a score.
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
        res = 0
        for ballot in profile:
            if proj in ballot:
                res += score_function(instance, ballot, [proj]) / proj.cost
        return res

    ordered_projects.sort(key=satisfaction_density, reverse=True)

    selection = []
    remaining_budget = instance.budget_limit - total_cost(budget_allocation)
    for project in ordered_projects:
        if project.cost <= remaining_budget:
            selection.append(project)
            remaining_budget -= project.cost

    if resoluteness:
        return selection

    cost_last_project = selection[-1].cost
    n_selected_tied_projects = 0
    for project in selection:
        if project.cost == cost_last_project:
            n_selected_tied_projects += 1

    tied_projects = []
    for project in ordered_projects:
        if project.cost == cost_last_project:
            tied_projects.append(project)

    selections = []
    for tail in fixed_size_subsets(tied_projects, n_selected_tied_projects):
        new_selection = copy(selection[:-n_selected_tied_projects])
        new_selection += list(tail)
        selections.append(selection)
    return selections


def greedy_welfare_approval(instance, profile, satisfaction, tie_breaking=LEXICO_TIE_BREAKING, resoluteness=True,
                            initial_budget_allocation=None):
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
            satisfaction : pbvoting.instance.satisfaction.SatisfactionFunction
                The satisfaction function used to define the social welfare.
            tie_breaking : pbvoting.rules.tiebreaking.TieBreakingRule, optional
                The tie-breaking rule used.
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

    if isinstance(satisfaction, AdditiveSatisfactionFunction):
        return greedy_scheme_additive_satisfaction(instance, profile, budget_allocation, satisfaction.sat, tie_breaking,
                                                   resoluteness=resoluteness)

    return greedy_scheme(instance, profile, budget_allocation, satisfaction.sat, tie_breaking,
                         resoluteness=resoluteness)
