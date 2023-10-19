"""
Positional satisfaction measures.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from numbers import Number

from pabutools.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pabutools.election.ballot import AbstractOrdinalBallot
from pabutools.election.instance import Instance, Project

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pabutools.election.profile import AbstractProfile


class PositionalSatisfaction(SatisfactionMeasure):
    """
    Class representing satisfaction measures that are based on the position of the projects in an ordinal ballot.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ordinalballot.AbstractOrdinalBallot`
            The ballot.
        positional_func : Callable[[:py:class:`~pabutools.election.ballot.ordinalballot.AbstractOrdinalBallot`, :py:class:`~pabutools.election.instance.Project`], Number]
            The positional function mapping ordinal ballots and projects to numbers. That represents the actual
            satisfaction function.
        aggregation_func : Callable[[Iterable[Number]], Number]
            The aggregation function used to aggregate the positional scores for a collection of projects.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ordinalballot.AbstractOrdinalBallot`
            The ballot.
        positional_func : Callable[[:py:class:`~pabutools.election.ballot.ordinalballot.AbstractOrdinalBallot`, :py:class:`~pabutools.election.instance.Project`], Number]
            The positional function mapping ordinal ballots and projects to numbers. That represents the actual
            satisfaction function.
        aggregation_func : Callable[[Iterable[Number]], Number]
            The aggregation function used to aggregate the positional scores for a collection of projects.
    """

    def __init__(
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractOrdinalBallot,
        positional_func: Callable[[AbstractOrdinalBallot, Project], Number],
        aggregation_func: Callable[[Iterable[Number]], Number],
    ):
        SatisfactionMeasure.__init__(self, instance, profile, ballot)
        self.positional_func = positional_func
        self.aggregation_func = aggregation_func
        self.instance = instance

    def sat(self, projects: Iterable[Project]):
        scores = [self.positional_func(self.ballot, project) for project in projects]
        return self.aggregation_func(scores)

    def sat_project(self, project: Project) -> Number:
        return self.sat([project])


def borda_sat_func(ballot: AbstractOrdinalBallot, project: Project) -> int:
    """
    Returns the Borda score of the project. If the project does not appear in the ballot, 0 is returned.

    Parameters
    ----------
        ballot: :py:class:`~pabutools.election.ballot.ballot.AbstractOrdinalBallot`
            The ordinal ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The project.

    Returns
    -------
        int
            The Borda score of the projects.

    """
    if project in ballot:
        return len(ballot) - ballot.index(project) - 1
    return 0


class Additive_Borda_Sat(PositionalSatisfaction):
    """
    Additive Borda satisfaction. It can only be applied to ordinal ballots. It is equal to the sum of the Borda scores
    of the selected projects in the ballots. The Borda score is the length of the ballot minus 1 plus the index of the
    project in the ballot

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ordinalballot.AbstractOrdinalBallot`
            The ballot.
    """

    def __init__(
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractOrdinalBallot,
    ):
        if isinstance(ballot, AbstractOrdinalBallot):
            PositionalSatisfaction.__init__(
                self, instance, profile, ballot, borda_sat_func, sum
            )
        else:
            raise ValueError(
                "The additive Borda satisfaction cannot be used for ballots of type {}".format(
                    type(ballot)
                )
            )
