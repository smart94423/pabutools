import numpy as np

from numbers import Number

from pabutools.election.instance import Instance, total_cost
from pabutools.election.profile import (
    Profile,
    MultiProfile,
    ApprovalProfile,
    ApprovalMultiProfile,
    CardinalProfile,
    CardinalMultiProfile,
    CumulativeProfile,
    CumulativeMultiProfile
)

from pabutools.fractions import frac
from pabutools.utils import mean_generator


def avg_ballot_length(instance: Instance, profile: Profile | MultiProfile) -> Number:
    """average ballot length in a profile"""
    return mean_generator((len(ballot), profile.multiplicity(ballot)) for ballot in profile)


def median_ballot_length(instance: Instance, profile: Profile | MultiProfile) -> int:
    """median ballot length in a profile"""
    ballot_lengths = np.zeros(profile.total_len())
    index = 0
    for ballot in profile:
        for j in range(profile.multiplicity(ballot)):
            ballot_lengths[index] = len(ballot)
            index += 1
    return np.median(ballot_lengths)


def avg_ballot_cost(instance: Instance, profile: ApprovalProfile | ApprovalMultiProfile) -> Number:
    """average ballot cost in an approval profile"""
    return mean_generator((total_cost(ballot), profile.multiplicity(ballot)) for ballot in profile)


def median_ballot_cost(instance: Instance, profile: ApprovalProfile | ApprovalMultiProfile) -> Number:
    """median ballot cost in an approval profile"""
    ballot_costs = np.zeros(profile.total_len())
    index = 0
    for ballot in profile:
        for j in range(profile.multiplicity(ballot)):
            ballot_costs[index] = total_cost(ballot)
            index += 1
    return np.median(ballot_costs)


def avg_approval_score(instance: Instance, profile: ApprovalProfile | ApprovalMultiProfile) -> Number:
    """average approval score of all projects in the instance"""
    return mean_generator(profile.approval_score(project) for project in instance)


def median_approval_score(instance: Instance, profile: ApprovalProfile | ApprovalMultiProfile) -> Number:
    """median approval score of all projects in the instance"""
    return np.median([frac(profile.approval_score(project)) for project in instance])


def avg_total_score(
    instance: Instance, profile: CumulativeProfile | CumulativeMultiProfile | CardinalProfile | CardinalMultiProfile
) -> Number:
    """average score of all projects in the instance"""
    return mean_generator(profile.score(project) for project in instance)


def median_total_score(
    instance: Instance, profile: CumulativeProfile | CumulativeMultiProfile | CardinalProfile | CardinalMultiProfile
) -> Number:
    """median score of all projects in the instance"""
    return np.median([frac(profile.score(project)) for project in instance])
