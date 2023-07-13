from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from pabutools.election.instance import Instance, Project
from pabutools.election.ballot import Ballot

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pabutools.election.profile import Profile


class SatisfactionMeasure(ABC):
    """
    Abstract class representing a satisfaction function. Only meant to be inherited.

    Parameters
    ----------
        instance : pabutools.election.instance.Instance
            The instance.
        profile : pabutools.instance.profile.Profile
            The profile.
        ballot : pabutools.instance.profile.Ballot
            The ballot.
    """

    def __init__(self, instance: Instance, profile: Profile, ballot: Ballot) -> None:
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
    def sat(self, projects: Iterable[Project]) -> float:
        """
        Returns the satisfaction of a voter with a given approval ballot for a given subset of projects.
        Parameters
        ----------
            projects : iterable of pabutools.election.instance.Project
                The set of projects.
        Returns
        -------
            float
        """


class GroupSatisfactionMeasure(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def multiplicity(self, sat: SatisfactionMeasure) -> int:
        ...
