import numpy as np
from pbvoting.instance.pbinstance import *
from pbvoting.instance.profile import *
from ..fractions import as_frac


def avg_ballot_length(profile: Profile) -> int:
    """average ballot length in a profile"""
    return np.average([as_frac(len(ballot)) for ballot in profile])


def median_ballot_length(profile: Profile) -> int:
    """median ballot length in a profile"""
    return np.median([len(ballot) for ballot in profile])


def ballot_cost(ballot: ApprovalBallot) -> Fraction:
    """total cost of all projects in an approval ballot"""
    return np.sum([project.cost for project in ballot])


def avg_ballot_cost(profile: ApprovalProfile) -> Fraction:
    """average ballot cost in an approval profile"""
    return np.average([ballot_cost(ballot) for ballot in profile])


def median_ballot_cost(profile: ApprovalProfile) -> Fraction:
    """median ballot cost in an approval profile"""
    return np.median([ballot_cost(ballot) for ballot in profile])
