from collections.abc import Iterable
from numbers import Number

import numpy as np
import math

from pbvoting.election.instance import Instance, Project
from pbvoting.election.profile import ApprovalProfile, Profile
from pbvoting.election.satisfaction import SatisfactionMeasure, CC_Sat, SatisfactionProfile
from pbvoting.fractions import frac

from pbvoting.utils import gini_coefficient, mean_generator


def avg_satisfaction(
    instance: Instance,
    profile: ApprovalProfile,
    budget_allocation: Iterable[Project],
    satisfaction: type[SatisfactionMeasure],
) -> Number | float:
    """Computes the average satisfaction for a given instance, profile and satisfaction function
    Parameters
    ----------
        instance : pbvoting.instance.pbinstance.PBInstance
            The instance.
        profile : pbvoting.instance.profile.ApprovalProfile
            The profile.
        budget_allocation : collection of pbvoting.instance.pbinstance.Project
            Collection of projects
        satisfaction : class
            The class defining the satisfaction function used to measure the social welfare. It should be a class
            inhereting from pbvoting.instance.satisfaction.Satisfaction.
    Returns
    -------
        average satisfaction"""

    return mean_generator(
        satisfaction(instance, profile, ballot).sat(budget_allocation)
        for ballot in profile
    )


def percent_non_empty_handed(
    instance: Instance, profile: ApprovalProfile, budget_allocation: Iterable[Project]
) -> Number | float:
    return avg_satisfaction(instance, profile, budget_allocation, CC_Sat)


def gini_coefficient_of_satisfaction(
    instance: Instance,
    profile: ApprovalProfile,
    budget_allocation: Iterable[Project],
    satisfaction: type[SatisfactionMeasure],
    invert: bool = False,
) -> Number | float:
    voter_satisfactions = np.array(
        [
            frac(satisfaction(instance, profile, ballot).sat(budget_allocation))
            for ballot in profile
        ]
    )
    if invert:
        return 1 - gini_coefficient(voter_satisfactions)
    return gini_coefficient(voter_satisfactions)

def satisfaction_histogram(
    instance: Instance,
    profile: Profile,
    budget_allocation: Iterable[Project],
    satisfaction: type[SatisfactionMeasure],
    max_satisfaction: float,
    num_bins: int = 20
) -> list[float]:
    sat_profile = SatisfactionProfile(instance=instance, profile=profile, sat_class=satisfaction)
    hist_data = [0.0 for i in range(num_bins)]
    for i in range(len(sat_profile)):
        satisfaction = sat_profile[i].sat(budget_allocation)
        
        if satisfaction > 1:
            raise ValueError("encountered satisfaction bigger than max_satisfaction")
        elif satisfaction == 1:
            hist_data[-1] += 1
        else:
            hist_data[math.floor(satisfaction*num_bins/max_satisfaction)] += 1
    for i in range(len(hist_data)):
        hist_data[i] = hist_data[i]/len(profile)
    return hist_data