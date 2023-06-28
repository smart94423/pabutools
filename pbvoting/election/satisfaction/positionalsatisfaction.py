from collections.abc import Callable, Iterable
from numbers import Number

from pbvoting.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pbvoting.election.ballot import OrdinalBallot
from pbvoting.election.instance import Instance, Project
from pbvoting.election.profile import Profile


class PositionalSatisfaction(SatisfactionMeasure):
    """
        Class representing satisfaction functions that are based on the position of the projects in an ordinal ballot.
        For a set of projects, the total satisfaction is additive.
    Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            ballot : pbvoting.instance.profile.OrdinalBallot
                The ordinal ballot.
            func : function
                A function taking as input an instance, a ballot and a subset of projects, and returning the score
                as a fraction.
        Attributes
        ----------
            func : function
                A function taking as input an instance, a profile, a ballot and a subset of projects, and returning the
                score of the subset of projects as a fraction.
    """

    def __init__(self,
                 instance: Instance,
                 profile: Profile,
                 ballot: OrdinalBallot,
                 positional_func: Callable[[OrdinalBallot, Project], Number],
                 aggregation_func: Callable[[Iterable[Number]], Number]):
        super(PositionalSatisfaction, self).__init__(instance, profile, ballot)
        self.positional_func = positional_func
        self.aggregation_func = aggregation_func
        self.instance = instance

    def sat(self,
            projects: Iterable[Project]):
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
        scores = [self.positional_func(self.ballot, project) for project in projects]
        return self.aggregation_func(scores)


def borda_sat_func(ballot: OrdinalBallot, project: Project) -> int:
    if project not in ballot:
        return 0
    return len(ballot) - ballot.index(project) - 1


class Additive_Borda_Sat(PositionalSatisfaction):

    def __init__(self, instance: Instance, profile: Profile, ballot: OrdinalBallot):
        super(Additive_Borda_Sat, self).__init__(instance, profile, ballot, borda_sat_func, sum)
