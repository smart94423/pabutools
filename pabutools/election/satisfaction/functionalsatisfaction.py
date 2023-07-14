from __future__ import annotations

from collections.abc import Callable, Iterable
from numbers import Number

import numpy as np

from pabutools.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pabutools.election.ballot import (
    AbstractBallot,
    ApprovalBallot,
    FrozenApprovalBallot,
    CardinalBallot,
    FrozenCardinalBallot,
)
from pabutools.election.instance import Instance, Project, total_cost

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pabutools.election.profile import (
        Profile,
        AbstractProfile,
        AbstractApprovalProfile,
        AbstractCardinalProfile,
    )


class FunctionalSatisfaction(SatisfactionMeasure):
    """
    Class representing satisfaction measures that are simply defined via functions of the ballot and a subset of
    projects.


    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        func : Callable[[:py:class:`~pabutools.election.instance.Instance`, :py:class:`~pabutools.election.profile.profile.AbstractProfile`, :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`, Iterable[:py:class:`~pabutools.election.instance.Project`], Number]
            The actual satisfaction function, i.e., a function returning the satisfaction for a given collection of
            projects, given the instance, the profile and the ballot under consideration.

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
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractBallot,
        func: Callable[
            [Instance, AbstractProfile, AbstractBallot, Iterable[Project]], Number
        ],
    ):
        SatisfactionMeasure.__init__(self, instance, profile, ballot)
        self.func = func

    def sat(self, projects: Iterable[Project]) -> Number:
        return self.func(self.instance, self.profile, self.ballot, projects)


def cc_sat_func_app(
    instance: Instance,
    profile: AbstractApprovalProfile,
    ballot: ApprovalBallot,
    projects: Iterable[Project],
) -> int:
    """
    Computes the Chamberlin-Courant satisfaction for approval ballots. It is equal to 1 if at least one approved project
    has been selected, and 0 otherwise.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.approvalprofile.AbstractApprovalProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.approvalballot.ApprovalBallot`
            The ballot.
        projects : Iterable[:py:class:`~pabutools.election.instance.Project`]
            The selected collection of projects.

    Returns
    -------
        int
            The Chamberlin-Courant satisfaction.

    """
    return int(any(p in ballot for p in projects))


def cc_sat_func_card(
    instance: Instance,
    profile: AbstractCardinalProfile,
    ballot: CardinalBallot,
    projects: Iterable[Project],
) -> Number:
    """
    Computes the Chamberlin-Courant satisfaction for approval ballots. It is equal to the maximum score assigned to
    a selected project in the ballot, and 0 if no selected project has been assigned a score.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.approvalprofile.AbstractApprovalProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.approvalballot.ApprovalBallot`
            The ballot.
        projects : Iterable[:py:class:`~pabutools.election.instance.Project`]
            The selected collection of projects.

    Returns
    -------
        Number
            The Chamberlin-Courant satisfaction.

    """
    res = 0
    for p in projects:
        if p in ballot and ballot[p] > res:
            res = ballot[p]
    return res


class CC_Sat(FunctionalSatisfaction):
    def __init__(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractBallot
    ):
        if isinstance(ballot, ApprovalBallot) or isinstance(
            ballot, FrozenApprovalBallot
        ):
            FunctionalSatisfaction.__init__(
                self, instance, profile, ballot, cc_sat_func_app
            )
        elif isinstance(ballot, CardinalBallot) or isinstance(
            ballot, FrozenCardinalBallot
        ):
            FunctionalSatisfaction.__init__(
                self, instance, profile, ballot, cc_sat_func_card
            )
        else:
            raise ValueError(
                "The Chamberlin-Courant satisfaction cannot be used for ballots for type {}".format(
                    type(ballot)
                )
            )


def cost_sqrt_sat_func(
    instance: Instance,
    profile: Profile,
    ballot: ApprovalBallot,
    projects: Iterable[Project],
) -> Number:
    return np.sqrt(float(total_cost([p for p in projects if p in ballot])))


class Cost_Sqrt_Sat(FunctionalSatisfaction):
    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(Cost_Sqrt_Sat, self).__init__(
            instance, profile, ballot, cost_sqrt_sat_func
        )


def cost_log_sat_func(
    instance: Instance,
    profile: Profile,
    ballot: ApprovalBallot,
    projects: Iterable[Project],
) -> Number:
    return np.log(float(1 + total_cost([p for p in projects if p in ballot])))


class Cost_Log_Sat(FunctionalSatisfaction):
    def __init__(self, instance, profile, ballot: ApprovalBallot):
        super(Cost_Log_Sat, self).__init__(instance, profile, ballot, cost_log_sat_func)
