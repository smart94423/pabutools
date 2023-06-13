
import numpy as np
from fractions import Fraction
from collections.abc import Callable, Iterable

from pbvoting.fractions import as_frac, frac
from pbvoting.instance.pbinstance import PBInstance, Project, total_cost
from pbvoting.instance.profile import Profile, Ballot, ApprovalBallot, OrdinalBallot


class Satisfaction:
    """
        Abstract class representing a satisfaction function. Only meant to be inherited.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            ballot : pbvoting.instance.profile.Ballot
                The ballot.
    """

    def __init__(self, instance: PBInstance, profile: Profile, ballot: Ballot):
        self.instance = instance
        self.profile = profile
        self.ballot = ballot

    def sat(self, projects: Iterable[Project]) -> float:
        """
            Returns the satisfaction of a voter with a given approval ballot for a given subset of projects.
            Parameters
            ----------
                projects : iterable of pbvoting.instance.pbinstance.Project
                    The set of projects.
            Returns
            -------
                float
        """


class SatisfactionProfile(list):
    """
        A profile of satisfaction functions, one per voter.
        Attributes
        ----------
    """

    def __init__(self, iterable=(), instance=None):
        super(SatisfactionProfile, self).__init__(iterable=iterable)
        self.instance = instance

    def __add__(self, value):
        return Profile(list.__add__(self, value), instance=self.instance)

    def __mul__(self, value):
        return Profile(list.__mul__(self, value), instance=self.instance)


class FunctionalSatisfaction(Satisfaction):
    """
        Class representing satisfaction functions simply defined via functions of the ballot and a subset of projects.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            ballot : pbvoting.instance.profile.ApprovalBallot
                The approval ballot.
            func : function
                A function taking as input an instance, a ballot and a subset of projects, and returning the score
                as a fraction.
        Attributes
        ----------
            func : function
                A function taking as input an instance, a profile, a ballot and a subset of projects, and returning the
                score of the subset of projects as a fraction.
    """

    def __init__(self, instance, profile, ballot: ApprovalBallot, func: Callable[[PBInstance, Profile, ApprovalBallot, set[Project]], Fraction]):
        super(FunctionalSatisfaction, self).__init__(instance, profile, ballot)
        self.func = func
        self.instance = instance

    def sat(self, projects):
        """
            Returns the satisfaction of a voter with a given approval ballot for a given subset of projects as defined
            by the inner function specified at initialisation.
            Parameters
            ----------
                projects : set of pbvoting.instance.pbinstance.Project
                    The set of projects.
            Returns
            -------
                float
        """
        return self.func(self.instance, self.profile, self.ballot, projects)


def cc_sat_func(instance: PBInstance, profile: Profile, ballot: ApprovalBallot, projects: set[Project]) -> Fraction:
    return as_frac(int(any(p in ballot for p in projects)))


class CC_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(CC_Sat, self).__init__(instance, profile, ballot, cc_sat_func)


def cost_sqrt_sat_func(instance: PBInstance, profile: Profile, ballot: ApprovalBallot, projects: set[Project]) -> Fraction:
    return as_frac(np.sqrt(total_cost([p for p in projects if p in ballot])))


class Cost_Sqrt_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(Cost_Sqrt_Sat, self).__init__(instance, profile, ballot, cost_sqrt_sat_func)


def log_sat_func(instance: PBInstance, profile: Profile, ballot: ApprovalBallot, projects: set[Project]) -> Fraction:
    return as_frac(np.log(1 + total_cost([p for p in projects if p in ballot])))


class Log_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(Log_Sat, self).__init__(instance, profile, ballot, log_sat_func)


class AdditiveSatisfaction(Satisfaction):
    """
        Class representing additive satisfaction functions, that is, satisfaction functions for which the total
        satisfaction is exactly the sum of the satisfaction of the individual projects. To speed up computations,
        scores are only computed once and for all.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            ballot : pbvoting.instance.profile.ApprovalBallot
                The approval ballot.
            func : function
                A function taking as input an instance, a profile, a ballot and a project, and returning
                the score as a fraction.
        Attributes
        ----------
            func : function
                A function taking as input an instance, a profile, a ballot and a project, and returning the score of
                the project as a fraction.
    """

    def __init__(self, instance: PBInstance, profile: Profile, ballot: ApprovalBallot, func: Callable[[PBInstance, Profile, ApprovalBallot, Project], Fraction]):
        super(AdditiveSatisfaction, self).__init__(instance, profile, ballot)
        self.func = func
        self.scores = dict()

    def get_score(self, project: Project) -> Fraction:
        if project in self.scores:
            return self.scores[project]
        score = self.func(self.instance, self.profile, self.ballot, project)
        self.scores[project] = score
        return score

    def sat(self, projects):
        """
            Returns the satisfaction of a voter with a given approval ballot for a given subset of projects. The
            satisfaction is additive, it is thus defines as the sum of the score of the projects under consideration.
            Parameters
            ----------
                projects : set of pbvoting.instance.pbinstance.Project
                    The set of projects.
            Returns
            -------
                float
        """
        return sum(self.get_score(project) for project in projects)


def cardinality_sat_func(instance: PBInstance, profile: Profile, ballot: ApprovalBallot, project: Project) -> Fraction:
    return as_frac(int(project in ballot))


class Cardinality_Sat(AdditiveSatisfaction):

    def __init__(self, instance: PBInstance, profile: Profile, ballot: ApprovalBallot):
        super(Cardinality_Sat, self).__init__(instance, profile, ballot, cardinality_sat_func)


def cost_sat_func(instance: PBInstance, profile: Profile, ballot: ApprovalBallot, project: Project) -> Fraction:
    return as_frac(int(project in ballot) * project.cost)


class Cost_Sat(AdditiveSatisfaction):

    def __init__(self, instance: PBInstance, profile: Profile, ballot: ApprovalBallot):
        super(Cost_Sat, self).__init__(instance, profile, ballot, cost_sat_func)


def effort_sat_func(instance: PBInstance, profile: Profile, ballot: ApprovalBallot, project: Project) -> Fraction:
    return frac(project.cost, sum(project in b for b in profile))


class Effort_Sat(AdditiveSatisfaction):

    def __init__(self, instance: PBInstance, profile: Profile, ballot: ApprovalBallot):
        super(Effort_Sat, self).__init__(instance, profile, ballot, effort_sat_func)


def additive_card_sat_func(instance: PBInstance, profile: Profile, ballot: ApprovalBallot, project: Project) -> Fraction:
    return ballot[project]


class Additive_Cardinal_Sat(AdditiveSatisfaction):

    def __init__(self, instance: PBInstance, profile: Profile, ballot: ApprovalBallot):
        super(Additive_Cardinal_Sat, self).__init__(instance, profile, ballot, additive_card_sat_func)


class PositionalSatisfaction(Satisfaction):
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

    def __init__(self, instance, profile, ballot: OrdinalBallot, positional_func: Callable[[OrdinalBallot, Project], float], aggregation_func: Callable[[Iterable[float]], float]):
        super(PositionalSatisfaction, self).__init__(instance, profile, ballot)
        self.positional_func = positional_func
        self.aggregation_func = aggregation_func
        self.instance = instance

    def sat(self, projects):
        """
            Returns the satisfaction of a voter with a given approval ballot for a given subset of projects as defined
            by the inner function specified at initialisation.
            Parameters
            ----------
                projects : set of pbvoting.instance.pbinstance.Project
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
    return len(ballot) - ballot.index(project)


class Additive_Borda_Sat(PositionalSatisfaction):

    def __init__(self, instance: PBInstance, profile: Profile, ballot: OrdinalBallot):
        super(Additive_Borda_Sat, self).__init__(instance, profile, ballot, borda_sat_func, sum)

