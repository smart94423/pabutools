from collections.abc import Iterable
from numbers import Number

from pabutools.election import Instance, AbstractApprovalProfile, Project, AbstractBallot, total_cost, \
    AbstractCardinalProfile, AbstractCardinalBallot, AbstractApprovalBallot, AbstractProfile
from pabutools.utils import powerset


def is_large_enough(group_size: int, num_voters: int, projects_cost: Number, budget_limit: Number) -> bool:
    return projects_cost * num_voters <= group_size * budget_limit


def is_cohesive_approval(
        instance: Instance,
        profile: AbstractApprovalProfile,
        projects: Iterable[Project],
        ballots: Iterable[AbstractApprovalBallot]
) -> bool:
    if not is_large_enough(profile.num_ballots(), sum(profile.multiplicity(b) for b in ballots), total_cost(projects), instance.budget_limit):
        return False
    if len(ballots) == 0 or len(projects) == 0:
        return False
    for ballot in ballots:
        for p in projects:
            if p not in ballot:
                return False
    return True


def is_cohesive_cardinal(
        instance: Instance,
        profile: AbstractCardinalProfile,
        projects: Iterable[Project],
        ballots: Iterable[AbstractCardinalBallot],
        alpha: dict[Project, Number]
) -> bool:
    if not is_large_enough(profile.num_ballots(), sum(profile.multiplicity(b) for b in ballots), total_cost(projects), instance.budget_limit):
        return False
    if len(ballots) == 0 or len(projects) == 0:
        return False
    for ballot in ballots:
        for p in projects:
            if ballot[p] > alpha[p]:
                return False
    return True


def cohesive_groups(instance: Instance, profile: AbstractProfile, projects=None):
    if projects is None:
        projects = instance
    res = []
    for group in powerset(profile):
        for project_set in powerset(projects):
            if isinstance(profile, AbstractApprovalProfile):
                if is_cohesive_approval(instance, profile, project_set, group):
                    res.append((group, project_set))
            elif isinstance(profile, AbstractCardinalProfile):
                alpha_min = {p: min(b[p] for b in profile) for p in project_set}
                if is_cohesive_cardinal(instance, profile, project_set, group, alpha_min):
                    res.append((group, project_set))
            else:
                raise NotImplementedError(f"We cannot find cohesive groups in a profile of type {type(profile)}. "
                                          f"Only approval and cardinal profiles are supported.")
    return res


def maximal_cohesive_for_projects_approval(
        instance: Instance,
        profile: AbstractApprovalProfile,
        projects: Iterable[Project]
) -> tuple[AbstractApprovalBallot]:
    res = []
    for ballot in profile:
        all_in = True
        for p in projects:
            if p not in ballot:
                all_in = False
                break
        if all_in:
            res.append(ballot)
    if len(res) > 0 and is_large_enough(len(res), profile.num_ballots(), total_cost(projects), instance.budget_limit):
        return tuple(res)


def maximal_cohesive_groups(
        instance: Instance,
        profile: AbstractProfile,
        projects: Iterable[Project] = None):
    if projects is None:
        projects = instance
    res = set()
    for project_set in powerset(projects):
        group = maximal_cohesive_for_projects_approval(instance, profile, project_set)
        if group:
            if isinstance(profile, AbstractApprovalProfile):
                if is_cohesive_approval(instance, profile, project_set, group):
                    res.add((group, project_set))
            else:
                raise NotImplementedError(f"We cannot find maximal cohesive groups in a profile of type "
                                          f"{type(profile)}. Only cardinal profiles are supported.")
    return res
