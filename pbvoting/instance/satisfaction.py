import numpy as np

from pbvoting.fractions import as_frac, frac
from pbvoting.instance.pbinstance import total_cost
from pbvoting.instance.profile import Profile


class Satisfaction:
    """
        Abstract class representing a satisfaction function. Only meant to be inherited.
        Parameters
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            ballot : pbvoting.instance.profile.ApprovalBallot
                The approval ballot.
    """

    def __init__(self, instance, profile, ballot):
        self.instance = instance
        self.profile = profile
        self.ballot = ballot

    def sat(self, projects):
        """
            Returns the satisfaction of a voter with a given approval ballot for a given subset of projects.
            Parameters
            ----------
                projects : set of pbvoting.instance.pbinstance.Project
                    The set of projects.
            Returns
            -------
                float
        """


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

    def __init__(self, instance, profile, ballot, func):
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
                A function taking as input an instance, a profile, a ballot and a subset of projects, and returning
                the score as a fraction.
        Attributes
        ----------
            func : function
                A function taking as input an instance, a profile, a ballot and a project, and returning the score of
                the project as a fraction.
    """

    def __init__(self, instance, profile, ballot, func):
        super(AdditiveSatisfaction, self).__init__(instance, profile, ballot)
        self.func = func
        self.scores = dict()

    def get_score(self, project):
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


def cardinality_sat_func(instance, profile, ballot, project):
    return as_frac(int(project in ballot))


class Cardinality_Sat(AdditiveSatisfaction):

    def __init__(self, instance, profile, ballot):
        super(Cardinality_Sat, self).__init__(instance, profile, ballot, cardinality_sat_func)


def cost_sat_func(instance, profile, ballot, project):
    return as_frac(int(project in ballot) * project.cost)


class Cost_Sat(AdditiveSatisfaction):

    def __init__(self, instance, profile, ballot):
        super(Cost_Sat, self).__init__(instance, profile, ballot, cost_sat_func)


def effort_sat_func(instance, profile, ballot, project):
    return frac(project.cost, sum(project in b for b in profile))


class Effort_Sat(AdditiveSatisfaction):

    def __init__(self, instance, profile, ballot):
        super(Effort_Sat, self).__init__(instance, profile, ballot, effort_sat_func)


def cc_sat_func(instance, profile, ballot, projects):
    return as_frac(int(any(p in ballot for p in projects)))


class CC_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot):
        super(CC_Sat, self).__init__(instance, profile, ballot, cc_sat_func)


def cost_sqrt_sat_func(instance, profile, ballot, projects):
    return as_frac(np.sqrt(total_cost([p for p in projects if p in ballot])))


class Cost_Sqrt_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot):
        super(Cost_Sqrt_Sat, self).__init__(instance, profile, ballot, cost_sqrt_sat_func)


def log_sat_func(instance, profile, ballot, projects):
    return as_frac(np.log(1 + total_cost([p for p in projects if p in ballot])))


class Log_Sat(FunctionalSatisfaction):

    def __init__(self, instance, profile, ballot):
        super(Log_Sat, self).__init__(instance, profile, ballot, log_sat_func)


class SatisfactionProfile(Profile):
    """
        A profile of satisfaction functions, one per voter.
         Inherits from `pbvoting.instance.profile.Profile`.
        Attributes
        ----------
    """

    def __init__(self, iterable=(), instance=None):
        super(SatisfactionProfile, self).__init__(iterable=iterable, instance=instance)
