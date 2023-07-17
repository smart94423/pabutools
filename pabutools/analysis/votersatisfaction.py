from collections.abc import Iterable
from numbers import Number

import numpy as np
import math

from pabutools.election.instance import Instance, Project
from pabutools.election.profile import ApprovalProfile, Profile
from pabutools.election.profile.profile import MultiProfile
from pabutools.election.satisfaction import (
    SatisfactionMeasure,
    CC_Sat,
    SatisfactionMultiProfile,
)
from pabutools.fractions import frac

from pabutools.utils import gini_coefficient, mean_generator


def avg_satisfaction(
    instance: Instance,
    profile: Profile | MultiProfile,
    budget_allocation: Iterable[Project],
    satisfaction: type[SatisfactionMeasure],
) -> Number | float:
    """Computes the average satisfaction for a given instance, profile and satisfaction function
    Parameters
    ----------
        instance : pabutools.instance.pbinstance.PBInstance
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile` | pabutools.instance.profile.MultiProfile
            The profile.
        budget_allocation : collection of pabutools.instance.pbinstance.Project
            Collection of projects
        satisfaction : class
            The class defining the satisfaction function used to measure the social welfare. It should be a class
            inhereting from pabutools.instance.satisfaction.Satisfaction.
    Returns
    -------
        average satisfaction"""

    return mean_generator(
        (
            satisfaction(instance, profile, ballot).sat(budget_allocation),
            profile.multiplicity(ballot),
        )
        for ballot in profile
    )


def percent_non_empty_handed(
    instance: Instance, profile: ApprovalProfile, budget_allocation: Iterable[Project]
) -> Number | float:
    return avg_satisfaction(instance, profile, budget_allocation, CC_Sat)


def gini_coefficient_of_satisfaction(
    instance: Instance,
    profile: Profile | MultiProfile,
    budget_allocation: Iterable[Project],
    satisfaction: type[SatisfactionMeasure],
    invert: bool = False,
) -> Number | float:
    voter_satisfactions = []
    for ballot in profile:
        voter_satisfaction = frac(
            satisfaction(instance, profile, ballot).sat(budget_allocation)
        )
        for i in range(profile.multiplicity(ballot)):
            voter_satisfactions.append(voter_satisfaction)

    if invert:
        return 1 - gini_coefficient(np.array(voter_satisfactions))
    return gini_coefficient(np.array(voter_satisfactions))


def satisfaction_histogram(
    instance: Instance,
    profile: Profile | MultiProfile,
    budget_allocation: Iterable[Project],
    satisfaction: type[SatisfactionMeasure],
    max_satisfaction: float,
    num_bins: int = 20,
) -> list[float]:
    if isinstance(profile, MultiProfile):
        sat_profile = SatisfactionMultiProfile(
            instance=instance, multiprofile=profile, sat_class=satisfaction
        )
    else:
        sat_profile = SatisfactionMultiProfile(
            instance=instance, profile=profile, sat_class=satisfaction
        )

    hist_data = [0.0 for i in range(num_bins)]
    for i, ballot in enumerate(sat_profile):
        satisfaction = ballot.sat(budget_allocation)
        if satisfaction >= max_satisfaction:
            hist_data[-1] += sat_profile.multiplicity(ballot)
        else:
            hist_data[
                math.floor(satisfaction * num_bins / max_satisfaction)
            ] += sat_profile.multiplicity(ballot)
    for i in range(len(hist_data)):
        hist_data[i] = hist_data[i] / profile.num_ballots()
    return hist_data
