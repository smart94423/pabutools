from collections.abc import Iterable
from fractions import Fraction

import numpy as np
from pbvoting.election.instance import Instance, Project
from pbvoting.election.profile import ApprovalProfile
from pbvoting.election.satisfaction import Satisfaction, SatisfactionProfile, CC_Sat
from pbvoting.utils import gini_coefficient


def avg_satisfaction(instance: Instance,
                     profile: ApprovalProfile,
                     budget_allocation: Iterable[Project],
                     satisfaction: type[Satisfaction]
                     ) -> Fraction | float:
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
    # if issubclass(type(satisfaction), Satisfaction):
    #     sat_profile = [satisfaction for ballot in profile]
    # else:
    #     sat_profile = satisfaction

    voter_satisfactions = np.array(
        [satisfaction(instance, profile, ballot).sat(budget_allocation) for ballot in profile])
    return np.mean(voter_satisfactions)


def percent_non_empty_handed(instance: Instance,
                             profile: ApprovalProfile,
                             budget_allocation: Iterable[Project]
                             ) -> Fraction | float:
    return avg_satisfaction(instance, profile, budget_allocation, CC_Sat)


def gini_coefficient_of_satisfaction(instance: Instance,
                                     profile: ApprovalProfile,
                                     budget_allocation: Iterable[Project],
                                     satisfaction: type[Satisfaction],
                                     invert: bool = False
                                     ) -> Fraction | float:
    voter_satisfactions = np.array(
        [satisfaction(instance, profile, ballot).sat(budget_allocation) for ballot in profile])
    if invert:
        return 1 - gini_coefficient(voter_satisfactions)
    return gini_coefficient(voter_satisfactions)
