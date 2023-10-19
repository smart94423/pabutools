"""
Additive satisfaction measures.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from numbers import Number

import numpy as np
from mip import Model, BINARY, maximize, xsum

from pabutools.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pabutools.election.ballot import (
    AbstractBallot,
    AbstractApprovalBallot,
    AbstractCardinalBallot,
)
from pabutools.election.instance import (
    Instance,
    Project,
    total_cost,
    max_budget_allocation_cardinality,
    max_budget_allocation_cost,
)
from pabutools.fractions import frac

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pabutools.election.profile import AbstractProfile


class AdditiveSatisfaction(SatisfactionMeasure):
    """
    Class representing additive satisfaction measures, that is, satisfaction functions for which the total
    satisfaction is exactly the sum of the satisfaction of the individual projects. To speed up computations,
    scores are only computed once and for all.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        func : Callable[[:py:class:`~pabutools.election.instance.Instance`, :py:class:`~pabutools.election.profile.profile.AbstractProfile`,  :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`, :py:class:`~pabutools.election.instance.Project`, dict[str, str]], Number]
            A function taking as input an instance, a profile, a ballot, a project and dictionary of precomputed values
            and returning the score of the project as a fraction.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        func : Callable[[:py:class:`~pabutools.election.instance.Instance`, :py:class:`~pabutools.election.profile.profile.AbstractProfile`,  :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`, :py:class:`~pabutools.election.instance.Project`, dict[str, str]], Number]
            A function taking as input an instance, a profile, a ballot, a project and dictionary of precomputed values
            and returning the score of the project as a fraction.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values. Initialised via the `preprocessing` method.
    """

    def __init__(
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractBallot,
        func: Callable[
            [Instance, AbstractProfile, AbstractBallot, Project, dict], Number
        ],
    ) -> None:
        SatisfactionMeasure.__init__(self, instance, profile, ballot)
        self.func = func
        self.scores = dict()
        self.precomputed_values = self.preprocessing(instance, profile, ballot)

    def preprocessing(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractBallot
    ) -> dict:
        """
        Preprocessing based on the instance, the profile and the ballot that returns a dictionary of precomputed
        values. The `precomputed_values` dictionary is initialised via this method.

        Parameters
        ----------
            instance : :py:class:`~pabutools.election.instance.Instance`
                The instance.
            profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
                The profile.
            ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
                The ballot.

        Returns
        -------
            dict[str, str]
                The precomputed values.
        """
        return {}

    def get_project_sat(self, project: Project) -> Number:
        """
        Given a project, computes the corresponding satisfaction. Stores the score after computation to avoid
        re-computing it.

        Parameters
        ----------
            project : :py:class:`~pabutools.election.instance.Project`
                The instance.

        Returns
        -------
            Number
                The satisfaction of the project.

        """
        return self.func(
            self.instance, self.profile, self.ballot, project, self.precomputed_values
        )
        score = self.scores.get(project, None)
        if score is None:
            score = self.func(
                self.instance,
                self.profile,
                self.ballot,
                project,
                self.precomputed_values,
            )
            self.scores[project] = score
        return score

    def sat(self, proj: Iterable[Project]) -> Number:
        return sum(self.get_project_sat(p) for p in proj)

    def sat_project(self, project: Project) -> Number:
        return self.get_project_sat(project)


def cardinality_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> int:
    """
    Computes the cardinality satisfaction for ballots. It is equal to 1 if the project is appears in the ballot and
    0 otherwise.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        int
            The cardinality satisfaction.
    """
    return int(project in ballot)


class Cardinality_Sat(AdditiveSatisfaction):
    """
    The cardinality satisfaction for ballots. It is equal to the number of selected projects appearing in the ballot.
    It applies to all ballot types that support the `in` operator.

    Parameters
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
    ):
        AdditiveSatisfaction.__init__(
            self, instance, profile, ballot, cardinality_sat_func
        )


def relative_cardinality_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> int:
    """
    Computes the relative cardinality satisfaction. If the project appears in the ballot, it is equal
    to 1 divided by the largest number of projects from the ballot that can be selected in any budget allocation. If the
    project does not appear in the ballot, or if the previous denominator is 0, then it is equal to 0.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The relative cardinality satisfaction.

    """
    if precomputed_values["max_budget_allocation_card"] == 0:
        return 0
    return frac(
        int(project in ballot), precomputed_values["max_budget_allocation_card"]
    )


class Relative_Cardinality_Sat(AdditiveSatisfaction):
    """
    The cardinality satisfaction for ballots. If the project appears in the ballot, it is equal
    to 1 divided by the largest number of projects from the ballot that can be selected in any budget allocation. If the
    project does not appear in the ballot, or if the previous denominator is 0, then it is equal to 0.
    It applies to all ballot types that support the `in` operator.

    Parameters
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
    ):
        AdditiveSatisfaction.__init__(
            self, instance, profile, ballot, relative_cardinality_sat_func
        )

    def preprocessing(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractBallot
    ):
        return {
            "max_budget_allocation_card": max_budget_allocation_cardinality(
                ballot, instance.budget_limit
            )
        }


def cost_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> int:
    """
    Computes the cost satisfaction for ballots. It is equal to the cost of the project if it appears in the
    ballot and 0 otherwise.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        int
            The cost satisfaction.
    """
    return int(project in ballot) * project.cost


class Cost_Sat(AdditiveSatisfaction):
    """
    The cost satisfaction for ballots. It is equal to the total cost of the selected projects appearing in the ballot.
    It applies to all ballot types that support the `in` operator.

    Parameters
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
    ):
        AdditiveSatisfaction.__init__(self, instance, profile, ballot, cost_sat_func)


def relative_cost_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the relative cost satisfaction for ballots. If the project appears in the ballot, it is equal to the cost
    of the project divided by the total cost of the most expensive subset of projects appearing in the ballot. It is
    0 if the project does not appear in the ballot.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The relative cost satisfaction.
    """
    if precomputed_values["max_budget_allocation_cost"] == 0:
        return 0
    return frac(
        int(project in ballot) * project.cost,
        precomputed_values["max_budget_allocation_cost"],
    )


class Relative_Cost_Sat(AdditiveSatisfaction):
    """
    The relative cost satisfaction for ballots. It is equal to the total cost of the selected projects appearing in the
    ballot, divided by the total cost of the most expensive subset of projects appearing in the ballot. It applies to
    all ballot types that support the `in` operator.

    Parameters
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
    ):
        AdditiveSatisfaction.__init__(
            self, instance, profile, ballot, relative_cost_sat_func
        )

    def preprocessing(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractBallot
    ):
        return {
            "max_budget_allocation_cost": max_budget_allocation_cost(
                ballot, instance.budget_limit
            )
        }


def relative_cost_approx_normaliser_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the relative cost satisfaction for ballots using an approximate normaliser: the minimum of the total cost of the projects
    appearing in the ballot and the total budget. See :py:func:`~pabutools.election.satisfaction.additivesatisfaction.relative_cost_sat_func`
    for the version with the exact normaliser.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The relative cost satisfaction with an approximate normaliser.
    """
    if precomputed_values["normalizer"] == 0:
        return 0
    return frac(int(project in ballot) * project.cost, precomputed_values["normalizer"])


class Relative_Cost_Approx_Normaliser_Sat(AdditiveSatisfaction):
    """
    The cost relative satisfaction for ballots, used with an approximate normaliser (since the exact version can take
    long to compute). It is equal to the total cost of the selected projects appearing in the ballot,
    divided by the total cost of the projects appearing in the ballot. It applies to all ballot types that support the
    `in` operator.

    Parameters
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
    ):
        AdditiveSatisfaction.__init__(
            self, instance, profile, ballot, relative_cost_approx_normaliser_sat_func
        )

    def preprocessing(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractBallot
    ):
        return {
            "normalizer": min(total_cost([p for p in ballot]), instance.budget_limit)
        }


def add_cost_sqrt_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the additive cost square root satisfaction for approval ballots. It is equal to the sum over the approved
    and selected projects of the square root of their costs.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The cost square root satisfaction of the project.

    """
    return int(project in ballot) * frac(np.sqrt(float(project.cost)))


class Additive_Cost_Sqrt_Sat(AdditiveSatisfaction):
    """
    Additive cost square root satisfaction. It is equal to the sum over the approved and selected projects of the square
    root of their costs. It can be applied to all ballot format supporting the `in` operator.

    Parameters
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
    ):
        if isinstance(ballot, AbstractApprovalBallot):
            AdditiveSatisfaction.__init__(
                self, instance, profile, ballot, add_cost_sqrt_sat_func
            )
        else:
            raise ValueError(
                "The cost square root satisfaction cannot be used with ballot types {}".format(
                    type(ballot)
                )
            )


def additive_cost_log_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the cost slog satisfaction for approval ballots. It is equal to the sum over the approved and selected
    projects of the log of 1 plus the cost of the projects.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.approvalballot.AbstractApprovalBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The log cost satisfaction of the project.

    """
    return int(project in ballot) * frac(np.log(1 + project.cost))


class Additive_Cost_Log_Sat(AdditiveSatisfaction):
    """
    Additive cost log satisfaction. It is equal to the sum over the approved and selected projects of the log of 1 plus
    the cost of the projects. It can be applied to all ballot format supporting the `in` operator.

    Parameters
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
    ):
        if isinstance(ballot, AbstractApprovalBallot):
            AdditiveSatisfaction.__init__(
                self, instance, profile, ballot, additive_cost_log_sat_func
            )
        else:
            raise ValueError(
                "The cost log satisfaction cannot be used with ballot types {}".format(
                    type(ballot)
                )
            )


def effort_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the effort satisfaction for ballots. If the project appears in the ballot, it is equal to the cost of the
    project, divided by the number of voters who included the project in their ballot.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The effort satisfaction.
    """
    denominator = sum(1 for b in profile if project in b)
    if denominator:
        return int(project in ballot) * frac(project.cost, denominator)
    return 0


class Effort_Sat(AdditiveSatisfaction):
    """
    The effort satisfaction. It is equal to the sum over the selected projects appearing in the
    ballot of the cost of the project divided by the number of voters who included the project in their ballot. It
    applies to all ballot types that support the `in` operator.

    Parameters
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
    ):
        AdditiveSatisfaction.__init__(self, instance, profile, ballot, effort_sat_func)


def additive_card_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractCardinalBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the additive satisfaction for cardinal ballots. It is equal to score assigned by the agent to the project.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.cardinalballot.AbstractCardinalBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The additive satisfaction for cardinal ballots.
    """
    return ballot.get(project, 0)


class Additive_Cardinal_Sat(AdditiveSatisfaction):
    """
    The additive satisfaction for cardinal ballots. It is equal to the sum over the selected projects appearing in the
    ballot of the score assigned to the project by the voter. It only applies to cardinal ballots.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.cardinalballot.AbstractCardinalBallot`
            The ballot.
    """

    def __init__(
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractCardinalBallot,
    ) -> None:
        if isinstance(ballot, AbstractCardinalBallot):
            AdditiveSatisfaction.__init__(
                self, instance, profile, ballot, additive_card_sat_func
            )
        else:
            raise ValueError(
                "The additive satisfaction for cardinal ballots cannot be used for ballots of type {}".format(
                    type(ballot)
                )
            )


def additive_card_relative_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractCardinalBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the relative additive satisfaction for cardinal ballots. It is equal to score assigned by the agent to the
    project, divided by the highest total score achievable by a feasible budget allocation.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.cardinalballot.AbstractCardinalBallot`
            The ballot.
        project : :py:class:`~pabutools.election.instance.Project`
            The selected project.
        precomputed_values : dict[str, str]
            A dictionary of precomputed values.

    Returns
    -------
        Number
            The relative additive satisfaction for cardinal ballots.
    """
    if precomputed_values["max_budget_allocation_score"] == 0:
        return 0
    return frac(
        ballot.get(project, 0), precomputed_values["max_budget_allocation_score"]
    )


class Additive_Cardinal_Relative_Sat(AdditiveSatisfaction):
    """
    The relative additive satisfaction for cardinal ballots. It is equal to the sum over the selected projects appearing
    in the ballot of the score assigned to the project by the voter, divided by the highest total score achievable by
    a feasible budget allocation. It only applies to cardinal ballots.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        ballot : :py:class:`~pabutools.election.ballot.cardinalballot.AbstractCardinalBallot`
            The ballot.
    """

    def __init__(
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractCardinalBallot,
    ) -> None:
        if isinstance(ballot, AbstractCardinalBallot):
            AdditiveSatisfaction.__init__(
                self, instance, profile, ballot, additive_card_relative_sat_func
            )
        else:
            raise ValueError(
                "The relative additive satisfaction for cardinal ballots cannot be used for ballots of type {}".format(
                    type(ballot)
                )
            )

    def preprocessing(
        self,
        instance: Instance,
        profile: AbstractProfile,
        ballot: AbstractCardinalBallot,
    ):
        res = 0
        mip_model = Model()
        mip_model.verbose = 0
        p_vars = {
            p: mip_model.add_var(var_type=BINARY, name="x_{}".format(p))
            for p in instance
        }
        if p_vars:
            mip_model.objective = maximize(
                xsum(p_vars[p] * ballot.get(p, 0) for p in instance)
            )
            mip_model += (
                xsum(p_vars[p] * p.cost for p in instance) <= instance.budget_limit
            )
            mip_model.optimize()
            res = mip_model.objective.x
        return {"max_budget_allocation_score": frac(res)}
