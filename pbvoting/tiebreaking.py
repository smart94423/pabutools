from collections.abc import Callable, Iterable
from fractions import Fraction

from pbvoting.instance.profile import Profile
from pbvoting.instance.pbinstance import PBInstance, Project


class TieBreakingRule:
    """
        Implements a tie-breaking rule.

        Parameters
        ----------
            func : Callable[[PBInstance, Profile, Project], Fraction]
            A function taking as input an instance, a profile and a project and returning the value on which the
            project will be sorted.

        Attributes
        ----------
            func : Callable[[PBInstance, Profile, Project], Fraction]
            A function taking as input an instance, a profile and a project and returning the value on which the
            project will be sorted.
    """

    def __init__(self, func: Callable[[PBInstance, Profile, Project], Fraction]):
        self.func = func

    def order(self,
              instance: PBInstance,
              profile: Profile,
              projects: Iterable[Project],
              key: Callable[..., Project] = lambda x: x):
        """
            Break the ties among all the projects provided in input and returns them ordered. The tie-breaking can be
            based on the instance or/and on the profile.
            Parameters
            ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.profile.Profile
                The profile.
            projects : collection of pbvoting.instance.pbinstance.Project
                The set of projects between which ties are to be broken.
            key : function[_ -> pbvoting.instance.pbinstance.Project]
                A key function to select the project from the input.
            Returns
            -------
                list of pbvoting.instance.pbinstance.Project
        """
        return sorted(list(projects), key=lambda project: self.func(instance, profile, key(project)))

    def untie(self,
              instance: PBInstance,
              profile: Profile,
              projects: Iterable[Project],
              key: Callable[..., Project] = lambda x: x):
        """
            Break the ties among all the projects provided in input and returns a single project. Orders the
            projects according to the tie-breaking rule and return the first project of the order.
            Parameters
            ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.profile.Profile
                The profile.
            projects : collection of pbvoting.instance.pbinstance.Project
                The set of projects between which ties are to be broken.
            key : function[_ -> pbvoting.instance.pbinstance.Project]
                A key function to select the project from the input.
            Returns
            -------
                pbvoting.instance.pbinstance.Project
        """
        return self.order(instance, profile, projects, key)[0]


lexico_tie_breaking = TieBreakingRule(lambda inst, prof, proj: proj.name)
app_score_tie_breaking = TieBreakingRule(lambda inst, prof, proj: -prof.approval_score(proj))
min_cost_tie_breaking = TieBreakingRule(lambda inst, prof, proj: proj.cost)
max_cost_tie_breaking = TieBreakingRule(lambda inst, prof, proj: -proj.cost)
