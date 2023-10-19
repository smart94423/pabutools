"""
Satisfaction measures.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable
from numbers import Number

from pabutools.election.ballot import AbstractBallot

from pabutools.election.instance import Instance, Project

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pabutools.election.profile import AbstractProfile


class SatisfactionMeasure(ABC):
    """
    Abstract class representing a satisfaction measure for a given ballot. Importantly, a satisfaction measure is always
    linked to a specific ballot, part of a specific profile, given a specific instance.

    Satisfaction measures are hased and compared based solely based on the ballot they correspond to. The profile and
    the instance are thus ignored.

    This class is only meant to be inherited.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.

    """

    def __init__(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractBallot
    ) -> None:
        self.instance = instance
        self.profile = profile
        self.ballot = ballot

    def __hash__(self):
        return self.ballot.__hash__()

    def __eq__(self, other):
        if isinstance(other, SatisfactionMeasure):
            return self.ballot == other.ballot
        return False

    def __le__(self, other):
        if isinstance(other, SatisfactionMeasure):
            return self.ballot <= other.ballot
        return False

    def __lt__(self, other):
        if isinstance(other, SatisfactionMeasure):
            return self.ballot < other.ballot
        return False

    def __str__(self):
        return "SAT[{}]".format(self.ballot)

    def __repr__(self):
        return "SAT[{}]".format(self.ballot)

    @abstractmethod
    def sat(self, projects: Iterable[Project]) -> Number:
        """
        Given the internal attributes of the satisfaction measure (ballot, profile, instance), returns the satisfaction
        for the given collection of projects.

        Parameters
        ----------
            projects : Iterable[:py:class:`~pabutools.election.instance.Project`]
                The collection of projects.

        Returns
        -------
            Number
                The corresponding satisfaction
        """

    @abstractmethod
    def sat_project(self, project: Project) -> Number:
        """
        Given the internal attributes of the satisfaction measure (ballot, profile, instance), returns the satisfaction
        for a single project.

        Parameters
        ----------
            project : :py:class:`~pabutools.election.instance.Project`
                The project.

        Returns
        -------
            Number
                The corresponding satisfaction
        """


class GroupSatisfactionMeasure(ABC, Iterable):
    """
    Abstract class representing a collection of satisfaction measure, one per voter.
    """

    def __init__(self):
        ABC.__init__(self)
        Iterable.__init__(self)

    @abstractmethod
    def multiplicity(self, sat: SatisfactionMeasure) -> int:
        """
        Returns the multiplicity of the given satisfaction measure.

        Parameters
        ----------
            sat : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`
                The satisfaction measure.

        Returns
        -------
            int
                The multiplicity of the satisfaction measure.
        """

    def total_satisfaction(self, projects: Iterable[Project]) -> Number:
        """
        Sums up the satisfaction of all the satisfaction measures for the given collection of projects.

        Parameters
        ----------
            projects : Iterable[:py:class:`~pabutools.election.instance.Project`]
                The collection of projects.

        Returns
        -------
            Number
                The total satisfaction for the collection of projects.

        """
        return sum(sat.sat(projects) * self.multiplicity(sat) for sat in self)

    def total_satisfaction_project(self, project: Project) -> Number:
        """
        Sums up the satisfaction of all the satisfaction measures for the given project.

        Parameters
        ----------
            project : :py:class:`~pabutools.election.instance.Project`
                The project.

        Returns
        -------
            Number
                The total satisfaction for the collection of projects.

        """
        return sum(sat.sat_project(project) * self.multiplicity(sat) for sat in self)

    @abstractmethod
    def remove_satisfied(
        self, sat_bound: dict[AbstractBallot, Number], projects: Iterable[Project]
    ) -> GroupSatisfactionMeasure:
        """
        Returns a new satisfaction profile excluding the satisfaction measurs corresponding to satisfied voters, i.e.,
        who have met or exceeded their satisfaction bound for a given collection of projects.

        Parameters
        ----------
            sat_bound : dict[str, Number]
                A dictionary of ballot names to numbers, specifying for each ballot the satisfaction bound above which
                the voter is considered satisfied. Note that the keys are ballot names, and that nothing ensures ballot
                names to be unique, so be careful here.
            projects : Iterable[:py:class:`~pabutools.election.instance.Project`]
                The collection of projects.

        Returns
        -------
            :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
                The new satisfaction profile.
        """
