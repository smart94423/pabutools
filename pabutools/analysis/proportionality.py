from collections.abc import Iterable

from pabutools.election import Instance, AbstractApprovalProfile, Project, AbstractBallot, total_cost
from pabutools.utils import powerset


def is_cohesive_approval(instance: Instance, profile: AbstractApprovalProfile, projects: Iterable[Project], ballots: Iterable[AbstractBallot]) -> bool:
    if total_cost(projects) * profile.num_ballots() > sum(profile.multiplicity(b) for b in ballots) * instance.budget_limit:
        return False
    if len(ballots) == 0 or len(projects) == 0:
        return False
    for ballot in ballots:
        for p in projects:
            if p not in ballot:
                return False
    return True


def cohesive_groups(instance, profile, projects=None):
    if projects is None:
        projects = instance
    res = set()
    for group in powerset(range(profile.num_ballots())):
        for projects in powerset(projects):
            if is_cohesive_approval(instance, profile, projects, group):
                res.add((group, projects))
    return res
