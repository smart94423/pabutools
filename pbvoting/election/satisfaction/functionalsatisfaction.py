from collections.abc import Callable, Iterable
from numbers import Number

import numpy as np

from pbvoting.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pbvoting.election.ballot import ApprovalBallot
from pbvoting.election.instance import Instance, Project, total_cost
from pbvoting.election.profile import Profile


class FunctionalSatisfaction(SatisfactionMeasure):
    """
        Class representing satisfaction functions simply defined via functions of the ballot and a subset of projects.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            ballot : pbvoting.instance.profile.Ballot
                The ballot.
            func : Callable[[PBInstance, Ballot, Profile, Iterable[Project]], Fraction]
                A function taking as input an instance, a ballot and a subset of projects, and returning the score
                as a fraction.
        Attributes
        ----------
            func : function
                A function taking as input an instance, a profile, a ballot and a subset of projects, and returning the
                score of the subset of projects as a fraction.
    """

    def __init__(self, instance, profile, ballot: ApprovalBallot,
                 func: Callable[[Instance, Profile, ApprovalBallot, Iterable[Project]], Number]):
        super(FunctionalSatisfaction, self).__init__(instance, profile, ballot)
        self.func = func
        self.instance = instance

    def sat(self, projects: Iterable[Project]):
        """
            Returns the satisfaction of a voter with a given approval ballot for a given subset of projects as defined
            by the inner function specified at initialisation.
            Parameters
            ----------
                projects : Iterable[pbvoting.instance.pbinstance.Project]
                    The set of projects.
            Returns
            -------
                float
        """
        return self.func(self.instance, self.profile, self.ballot, projects)


def cc_sat_func(instance: Instance,
                profile: Profile,
                ballot: ApprovalBallot,
                projects: Iterable[Project]
                ) -> Number:
    return int(any(p in ballot for p in projects))


class CC_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(CC_Sat, self).__init__(instance, profile, ballot, cc_sat_func)


def cost_sqrt_sat_func(instance: Instance,
                       profile: Profile,
                       ballot: ApprovalBallot,
                       projects: Iterable[Project]
                       ) -> Number:
    return np.sqrt(float(total_cost([p for p in projects if p in ballot])))


class Cost_Sqrt_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(Cost_Sqrt_Sat, self).__init__(instance, profile, ballot, cost_sqrt_sat_func)


def cost_log_sat_func(instance: Instance,
                      profile: Profile,
                      ballot: ApprovalBallot,
                      projects: Iterable[Project]
                      ) -> Number:
    return np.log(float(1 + total_cost([p for p in projects if p in ballot])))


class Cost_Log_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(Cost_Log_Sat, self).__init__(instance, profile, ballot, cost_log_sat_func)
