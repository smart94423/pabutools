from pbvoting.tiebreaking.approval import APPROVAL_TIE_BREAKING
from pbvoting.instance.satisfaction import cost_sat
from pbvoting.fractions import as_frac

from fractions import Fraction
from copy import copy



def contributions_w_alpha(instance, profile, satisfaction_func, project, leftover_budgets, alpha_limit=None):
    approvers = [voter for voter in range(len(profile)) if project in profile[voter]]
    if not affordable(project, approvers, leftover_budgets):
        return None

    all_contributions = dict()
    for voter in range(len(profile)):
        all_contributions[voter] = as_frac(0)

    rich = copy(approvers)
    total_poor_contribution = as_frac(0)
    cost = as_frac(project.cost)

    while True:
        rich_satisfactions = dict()
        for voter in rich:
            satisfaction = as_frac(satisfaction_func.sat(instance, profile[voter], {project}))
            rich_satisfactions[voter] = satisfaction
        alpha = Fraction(cost - total_poor_contribution, sum(rich_satisfactions.values()))
        if alpha_limit is not None and alpha > alpha_limit:
            return None
        for voter in rich:
            contribution = alpha * rich_satisfactions[voter]
            if contribution > leftover_budgets[voter]:
                rich.remove(voter)
                total_poor_contribution += leftover_budgets[voter]
                all_contributions[voter] = leftover_budgets[voter]
            else:
                all_contributions[voter] = contribution
        if sum(all_contributions.values()) >= cost:
            return all_contributions, alpha


def affordable(project, approvers, leftover_budgets):
    max_total_contribution = sum([leftover_budgets[voter] for voter in approvers])
    if max_total_contribution < project.cost:
        return False
    return True


def select_projects(instance, profile, satisfaction_func, leftover_budgets, allocation,
                    tiebreaking_rule=APPROVAL_TIE_BREAKING, resoluteness=True):
    minimal_alpha = None
    argmin = None
    for project in instance:
        if project not in allocation:
            pair = contributions_w_alpha(instance, profile, satisfaction_func, project, leftover_budgets,
                                         alpha_limit=minimal_alpha)
            if pair is None:
                continue
            else:
                all_contributions, alpha = pair

            if minimal_alpha is None or alpha < minimal_alpha:
                minimal_alpha = alpha
                argmin = [(project, all_contributions)]
            elif alpha == minimal_alpha:
                argmin.append((project, all_contributions))
    if resoluteness and argmin is not None:
        argmin = [tiebreaking_rule.order(instance, profile, argmin, lambda p: p[0])[0]]
    return argmin


def method_of_equal_shares_approval(instance, profile, satisfaction_func=cost_sat,
                                    initial_budget_allocation=(), tiebreaking_rule=APPROVAL_TIE_BREAKING,
                                    resoluteness=True):
    if not resoluteness:
        raise NotImplementedError

    leftover_budgets = [Fraction(int(instance.budget_limit), len(profile)) for _ in profile]
    allocation = list(initial_budget_allocation)
    while True:
        project_candidates = select_projects(instance, profile, satisfaction_func, leftover_budgets, allocation,
                                             tiebreaking_rule=tiebreaking_rule, resoluteness=resoluteness)

        if project_candidates is None:
            return allocation
        else:
            for project, all_contributions in project_candidates:
                allocation.append(project)
                for voter in range(len(profile)):
                    leftover_budgets[voter] -= all_contributions[voter]
