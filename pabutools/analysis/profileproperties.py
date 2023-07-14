import numpy as np

from numbers import Number

from pabutools.election.instance import Instance, total_cost
from pabutools.election.profile import (
    Profile,
    ApprovalProfile,
    CardinalProfile,
    CumulativeProfile,
)

from pabutools.fractions import frac
from pabutools.utils import mean_generator


def avg_ballot_length(instance: Instance, profile: Profile) -> Number:
    """average ballot length in a profile"""
    return mean_generator(len(ballot) for ballot in profile)


def median_ballot_length(instance: Instance, profile: Profile) -> int:
    """median ballot length in a profile"""
    return np.median([frac(len(ballot)) for ballot in profile])


def avg_ballot_cost(instance: Instance, profile: ApprovalProfile) -> Number:
    """average ballot cost in an approval profile"""
    return mean_generator(total_cost(ballot) for ballot in profile)


def median_ballot_cost(instance: Instance, profile: ApprovalProfile) -> Number:
    """median ballot cost in an approval profile"""
    return np.median([total_cost(ballot) for ballot in profile])


def avg_approval_score(instance: Instance, profile: ApprovalProfile) -> Number:
    """average approval score of all projects in the instance"""
    return mean_generator([profile.approval_score(project) for project in instance])


def median_approval_score(instance: Instance, profile: ApprovalProfile) -> Number:
    """median approval score of all projects in the instance"""
    return np.median([frac(profile.approval_score(project)) for project in instance])


def avg_total_score(
    instance: Instance, profile: CumulativeProfile | CardinalProfile
) -> Number:
    """average score of all projects in the instance"""
    return mean_generator(profile.total_score(project) for project in instance)


def median_total_score(
    instance: Instance, profile: CumulativeProfile | CardinalProfile
) -> Number:
    """median score of all projects in the instance"""
    return np.median([frac(profile.total_score(project)) for project in instance])
