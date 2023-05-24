from pbvoting.tiebreaking import lexico_tie_breaking
from pbvoting.tiebreaking.approval import app_score_tie_breaking
from pbvoting.instance.satisfaction import Cost_Sat
from pbvoting.fractions import as_frac, frac

from fractions import Fraction
from copy import copy


def mes_scheme(instance, profile, sat_profile, initial_budget, budget_allocation, tie_breaking, resoluteness=True):
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

    projects = set(instance)
    for project in budget_allocation:
        projects.remove(project)
    budgets = {i: initial_budget for i in range(len(profile))}
    selection = []
    total_scores = {proj: sum(sat.sat([proj]) for sat in sat_profile) for proj in projects}
    for project, score in total_scores.items():
        if score <= 0 or project.cost == 0:
            projects.remove(project)
    supporters = {proj: [i for i in range(len(profile)) if sat_profile[i].sat([proj]) > 0] for proj in projects}
    affordabilities = {proj: frac(proj.cost, total_scores[proj]) for proj in projects}
    while True:
        selected_project = None
        best_afford = float('inf')
        for project in sorted(projects, key=lambda proj: affordabilities[proj]):
            if affordabilities[project] > best_afford:
                break
            if sum(budgets[i] for i in supporters[project]) < project.cost: # unaffordable, can delete
                projects.remove(project)
                continue
            supporters[project].sort(key=lambda i: budgets[i] / sat_profile[i].sat([project]))
            paid_so_far = 0
            denominator = total_scores[project]
            for j in range(len(supporters[project])):
                rho = frac(project.cost - paid_so_far, denominator)
                if rho * sat_profile[supporters[project][j]].sat([project]) <= budgets[supporters[project][j]]:
                    # found best rho for this candidate
                    affordabilities[project] = rho
                    if rho < best_afford:
                        best_afford = rho
                        selected_project = project
                    break
                paid_so_far += budgets[supporters[project][j]]
                denominator -= sat_profile[supporters[project][j]].sat([project])
        if not selected_project:
            break
        selection.append(selected_project)
        projects.remove(selected_project)
        for i in supporters[selected_project]:
            budgets[i] -= min(budgets[i], best_afford * sat_profile[i].sat([selected_project]))

    return selection


def method_of_equal_shares(instance, profile, satisfaction=None, sat_profile=None, tie_breaking=lexico_tie_breaking,
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
            satisfaction : pbvoting.instance.satisfaction.Satisfaction
                The class defining the satisfaction function used to measure the social welfare. If no satisfaction
                is provided, a satisfaction profile needs to be provided. If a satisfation profile is provided, the
                satisfaction argument is disregarded.
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

    return mes_scheme(instance, profile, sat_profile, frac(instance.budget_limit, len(profile)), budget_allocation, tie_breaking,
                      resoluteness=resoluteness)
