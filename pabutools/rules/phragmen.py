"""
Phragmèn's methods.
"""
from collections.abc import Iterable
from copy import deepcopy
from numbers import Number

from pabutools.fractions import frac
from pabutools.election import (
    Instance,
    Project,
    total_cost,
    ApprovalProfile,
    ApprovalMultiProfile,
)
from pabutools.tiebreaking import TieBreakingRule, lexico_tie_breaking


class PhragmenVoter:
    def __init__(self, ballot, load, multiplicity):
        self.ballot = ballot
        self.load = load
        self.multiplicity = multiplicity

    def total_load(self):
        return self.multiplicity * self.load


def sequential_phragmen(
    instance: Instance,
    profile: ApprovalProfile | ApprovalMultiProfile,
    initial_loads: list[Number] = None,
    initial_budget_allocation: Iterable[Project] = None,
    tie_breaking: TieBreakingRule = lexico_tie_breaking,
    resoluteness: bool = True,
) -> list[Project] | list[list[Project]]:
    """
    The inner algorithm to compute the outcome of the sequential Phragmén's rule.
    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : pabutools.instance.profile.ApprovalProfile | pabutools.instance.profile.ApprovalMultiProfile
            The profile.
        initial_loads : list[Fraction]
            The initial load distribution of the voters.
        initial_budget_allocation : collection of pabutools.election.instance.Project
            An initial budget allocation, typically empty.
        tie_breaking : :py:class:`pabutools.tiebreaking.TieBreakingRule`
            The tie-breaking rule used.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
    Returns
    -------
        list of pabutools.election.instance.Project if resolute, list of the previous if irresolute
    """

    def aux(
        inst,
        projects,
        prof,
        voters,
        supporters,
        approval_scores,
        alloc,
        cost,
        allocs,
        resolute,
    ):
        if len(projects) == 0:
            alloc.sort()
            if alloc not in allocs:
                allocs.append(alloc)
        else:
            min_new_maxload = None
            arg_min_new_maxload = None
            for project in projects:
                if approval_scores[project] == 0:
                    new_maxload = float("inf")
                else:
                    new_maxload = frac(
                        sum(voters[i].total_load() for i in supporters[project])
                        + project.cost,
                        approval_scores[project],
                    )
                if min_new_maxload is None or new_maxload < min_new_maxload:
                    min_new_maxload = new_maxload
                    arg_min_new_maxload = [project]
                elif min_new_maxload == new_maxload:
                    arg_min_new_maxload.append(project)

            if any(
                cost + project.cost > inst.budget_limit
                for project in arg_min_new_maxload
            ):
                alloc.sort()
                if alloc not in allocs:
                    allocs.append(alloc)
            else:
                tied_projects = tie_breaking.order(inst, prof, arg_min_new_maxload)
                if resolute:
                    selected_project = tied_projects[0]
                    for voter in voters:
                        if selected_project in voter.ballot:
                            voter.load = min_new_maxload
                    alloc.append(selected_project)
                    projects.remove(selected_project)
                    aux(
                        inst,
                        projects,
                        prof,
                        voters,
                        supporters,
                        approval_scores,
                        alloc,
                        cost + selected_project.cost,
                        allocs,
                        resolute,
                    )
                else:
                    for selected_project in tied_projects:
                        new_voters = deepcopy(voters)
                        for voter in new_voters:
                            if selected_project in voter.ballot:
                                voter.load = min_new_maxload
                        new_alloc = deepcopy(alloc) + [selected_project]
                        new_cost = cost + selected_project.cost
                        new_projs = deepcopy(projects)
                        new_projs.remove(selected_project)
                        aux(
                            inst,
                            new_projs,
                            prof,
                            new_voters,
                            supporters,
                            approval_scores,
                            new_alloc,
                            new_cost,
                            allocs,
                            resolute,
                        )

    if initial_budget_allocation is None:
        initial_budget_allocation = []
    current_cost = total_cost(initial_budget_allocation)

    initial_projects = set(
        p
        for p in instance
        if p not in initial_budget_allocation and p.cost <= instance.budget_limit
    )

    if initial_loads is None:
        voters_details = [PhragmenVoter(b, 0, profile.multiplicity(b)) for b in profile]
    else:
        voters_details = [
            PhragmenVoter(b, initial_loads[i], profile.multiplicity(b))
            for i, b in enumerate(profile)
        ]
    supps = {
        proj: [i for i, v in enumerate(voters_details) if proj in v.ballot]
        for proj in initial_projects
    }

    scores = {project: profile.approval_score(project) for project in instance}

    all_budget_allocations = []
    aux(
        instance,
        initial_projects,
        profile,
        voters_details,
        supps,
        scores,
        initial_budget_allocation,
        current_cost,
        all_budget_allocations,
        resoluteness,
    )

    if resoluteness:
        return all_budget_allocations[0]
    return all_budget_allocations
