import numpy as np

from pbvoting.fractions import as_frac, frac
from pbvoting.instance.pbinstance import total_cost


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


def cardinality_sat(instance, profile, ballot):
    return AdditiveSatisfaction(instance, profile, ballot,
                                lambda inst, prof, ball, proj: as_frac(int(proj in ball)))


def cost_sat(instance, profile, ballot):
    return AdditiveSatisfaction(instance, profile, ballot,
                                lambda inst, prof, ball, proj: int(proj in ball) * proj.cost)


def effort_sat(instance, profile, ballot):
    return AdditiveSatisfaction(instance, profile, ballot,
                                lambda inst, prof, ball, proj: frac(proj.cost, sum(proj in b for b in prof)))


def cc_sat(instance, profile, ballot):
    return FunctionalSatisfaction(instance, profile, ballot,
                                  lambda inst, prof, ball, projs: as_frac(int(any(p in ball for p in projs))))


def cost_square_root_sat(instance, profile, ballot):
    return FunctionalSatisfaction(instance, profile, ballot,
                                  lambda inst, prof, ball, projs: as_frac(np.sqrt(
                                      total_cost([p for p in projs if p in ball]))))


def log_sat(instance, profile, ballot):
    return FunctionalSatisfaction(instance, profile, ballot,
                                  lambda inst, prof, ball, projs: as_frac(np.log(
                                      1 + total_cost([p for p in projs if p in ball]))))
