from collections.abc import Iterable
from copy import deepcopy
from fractions import Fraction

from pbvoting.fractions import number_as_frac, frac
from pbvoting.instance import PBInstance, Project, total_cost, ApprovalProfile
from pbvoting.tiebreaking import TieBreakingRule, lexico_tie_breaking


def sequential_phragmen(instance: PBInstance,
                        profile: ApprovalProfile,
                        initial_loads: list[Fraction] = None,
                        initial_budget_allocation: Iterable[Project] = None,
                        tie_breaking: TieBreakingRule = lexico_tie_breaking,
                        resoluteness: bool = True
                        ) -> list[Project] | list[list[Project]]:
    """
        The inner algorithm to compute the outcome of the sequential Phragmén's rule.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.ApprovalProfile
                The profile.
            sat_profile : pbvoting.instance.pbinstance.SatisfactionProfile
                The profile of satisfaction functions.
            initial_loads : list[Fraction]
                The initial load distribution of the voters.
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

    def aux(inst, prof, projs, load, scores, alloc, cost, allocs, resolute):
        if len(projs) == 0:
            alloc.sort()
            if alloc not in allocs:
                allocs.append(alloc)
        else:
            approvers_load = {project: sum(load[i] for i in range(len(prof)) if project in prof[i])
                              for project in projs}
            new_maxload = dict()
            for project in projs:
                if scores[project] == 0:
                    new_maxload[project] = float('inf')
                else:
                    new_maxload[project] = frac(approvers_load[project] + project.cost, scores[project])
            min_new_maxload = min(new_maxload.values())

            tied_projects = [project for project in projs if new_maxload[project] == min_new_maxload]
            new_cost = [cost + project.cost for project in tied_projects]
            if any(c > inst.budget_limit for c in new_cost):
                alloc.sort()
                if alloc not in allocs:
                    allocs.append(alloc)
            else:
                tied_projects = tie_breaking.order(instance, profile, tied_projects)
                if resolute:
                    selected_project = tied_projects[0]
                    for i in range(len(prof)):
                        if selected_project in prof[i]:
                            load[i] = new_maxload[selected_project]
                    alloc.append(selected_project)
                    projs.remove(selected_project)
                    aux(inst, prof, projs, load, scores, alloc, cost + selected_project.cost, allocs, resolute)
                else:
                    for selected_project in tied_projects:
                        new_load = deepcopy(load)
                        for i in range(len(prof)):
                            if selected_project in prof[i]:
                                new_load[i] = new_maxload[selected_project]
                        new_alloc = deepcopy(alloc) + [selected_project]
                        new_cost = cost + selected_project.cost
                        new_projs = deepcopy(projs)
                        new_projs.remove(selected_project)
                        aux(inst, prof, new_projs, new_load, scores, new_alloc, new_cost, allocs, resolute)

    if initial_loads is None:
        initial_loads = [number_as_frac(0) for _ in range(len(profile))]
    if initial_budget_allocation is None:
        initial_budget_allocation = []
    current_cost = total_cost(initial_budget_allocation)

    projects = set(p for p in instance if p not in initial_budget_allocation and p.cost <= instance.budget_limit)
    approval_scores = {project: profile.approval_score(project) for project in instance}

    all_budget_allocations = []
    aux(instance, profile, projects, initial_loads, approval_scores, initial_budget_allocation, current_cost,
        all_budget_allocations, resoluteness)

    if resoluteness:
        return all_budget_allocations[0]
    return all_budget_allocations
