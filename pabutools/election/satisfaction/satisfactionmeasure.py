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
        res = 0
        for sat in self:
            res += sat.sat(projects) * self.multiplicity(sat)
        return res
