import profile
import numpy as np
from pbvoting.instance.pbinstance import *
from pbvoting.instance.profile import *
from ..fractions import number_as_frac


def avg_ballot_length(instance: PBInstance, profile: Profile) -> Fraction:
    """average ballot length in a profile"""
    return np.average([number_as_frac(len(ballot)) for ballot in profile])


def median_ballot_length(instance: PBInstance, profile: Profile) -> int:
    """median ballot length in a profile"""
    return np.median([len(ballot) for ballot in profile])


def ballot_cost(ballot: ApprovalBallot) -> Fraction:
    """total cost of all projects in an approval ballot"""
    return np.sum([project.cost for project in ballot])


def avg_ballot_cost(instance: PBInstance, profile: ApprovalProfile) -> Fraction:
    """average ballot cost in an approval profile"""
    return np.average([ballot_cost(ballot) for ballot in profile])


def median_ballot_cost(instance: PBInstance, profile: ApprovalProfile) -> Fraction:
    """median ballot cost in an approval profile"""
    return np.median([ballot_cost(ballot) for ballot in profile])


def avg_approval_score(instance: PBInstance, profile: ApprovalProfile) -> Fraction:
    """average approval score of all projects in the instance"""
    return np.average([number_as_frac(profile.approval_score(project)) for project in instance])


def median_approval_score(instance: PBInstance, profile: ApprovalProfile) -> Fraction:
    """median approval score of all projects in the instance"""
    return np.median([profile.approval_score(project) for project in instance])


def avg_total_score(instance: PBInstance, profile: CumulativeProfile | CardinalProfile) -> Fraction:
    """average score of all projects in the instance"""
    return np.average([profile.score(project) for project in instance])


def median_total_score(instance: PBInstance, profile: CumulativeProfile | CardinalProfile) -> Fraction:
    """median score of all projects in the instance"""
    return np.median([profile.score(project) for project in instance])
