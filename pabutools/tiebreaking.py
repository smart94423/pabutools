from collections.abc import Callable, Iterable
from numbers import Number

from pabutools.election.profile import Profile
from pabutools.election.instance import Instance, Project


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

    def __init__(self, func: Callable[[Instance, Profile, Project], Number]):
        self.func = func

    def order(
        self,
        instance: Instance,
        profile: Profile,
        projects: Iterable[Project],
        key: Callable[..., Project] = lambda x: x,
    ):
        """
        Break the ties among all the projects provided in input and returns them ordered. The tie-breaking can be
        based on the instance or/and on the profile.
        Parameters
        ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : pabutools.profile.Profile
            The profile.
        projects : collection of pabutools.election.instance.Project
            The set of projects between which ties are to be broken.
        key : function[_ -> pabutools.election.instance.Project]
            A key function to select the project from the input.
        Returns
        -------
            list of pabutools.election.instance.Project
        """
        return sorted(
            list(projects),
            key=lambda project: self.func(instance, profile, key(project)),
        )

    def untie(
        self,
        instance: Instance,
        profile: Profile,
        projects: Iterable[Project],
        key: Callable[..., Project] = lambda x: x,
    ):
        """
        Break the ties among all the projects provided in input and returns a single project. Orders the
        projects according to the tie-breaking rule and return the first project of the order.
        Parameters
        ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : pabutools.profile.Profile
            The profile.
        projects : collection of pabutools.election.instance.Project
            The set of projects between which ties are to be broken.
        key : function[_ -> pabutools.election.instance.Project]
            A key function to select the project from the input.
        Returns
        -------
            pabutools.election.instance.Project
        """
        return self.order(instance, profile, projects, key)[0]


lexico_tie_breaking = TieBreakingRule(lambda inst, prof, proj: proj.name)
app_score_tie_breaking = TieBreakingRule(
    lambda inst, prof, proj: -prof.approval_score(proj)
)
min_cost_tie_breaking = TieBreakingRule(lambda inst, prof, proj: proj.cost)
max_cost_tie_breaking = TieBreakingRule(lambda inst, prof, proj: -proj.cost)
