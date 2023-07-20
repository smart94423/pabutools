"""
Additive satisfaction measures.
"""
from __future__ import annotations

from collections.abc import Callable, Iterable
from numbers import Number

from pabutools.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pabutools.election.ballot import (
    AbstractBallot,
    AbstractApprovalBallot,
    AbstractCardinalBallot,
)
from pabutools.election.instance import Instance, Project, total_cost
from pabutools.fractions import frac

from typing import TYPE_CHECKING

from mip import Model, xsum, maximize, BINARY

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
        if project in self.scores:
            return self.scores[project]
        score = self.func(
            self.instance, self.profile, self.ballot, project, self.precomputed_values
        )
        self.scores[project] = score
        return score

    def sat(self, projects: Iterable[Project]) -> Number:
        return sum(self.get_project_sat(project) for project in projects)


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
        ballot_sorted = sorted(ballot, key=lambda proj: proj.cost)
        cost = 0
        selected = 0
        for p in ballot_sorted:
            new_total_cost = p.cost + cost
            if new_total_cost > instance.budget_limit:
                break
            cost = new_total_cost
            selected += 1
        return {"max_budget_allocation_card": selected}


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
        mip_model = Model()
        mip_model.verbose = 0
        p_vars = {
            p: mip_model.add_var(var_type=BINARY, name="x_{}".format(p)) for p in ballot
        }
        if p_vars:
            mip_model.objective = maximize(xsum(p_vars[p] * p.cost for p in ballot))
            mip_model += (
                xsum(p_vars[p] * p.cost for p in ballot) <= instance.budget_limit
            )
            mip_model.optimize()
            max_cost = mip_model.objective.x
            return {"max_budget_allocation_cost": frac(max_cost)}
        return {"max_budget_allocation_cost": 0}


def relative_cost_approx_normaliser_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    """
    Computes the relative cost satisfaction for ballots using an approximate normaliser: the total cost of the projects
    appearing in the ballot. See :py:func:`~pabutools.election.satisfaction.additivesatisfaction.relative_cost_sat_func`
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
    if precomputed_values["total_ballot_cost"] == 0:
        return 0
    return frac(
        int(project in ballot) * project.cost, precomputed_values["total_ballot_cost"]
    )


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
        return {"total_ballot_cost": total_cost([p for p in ballot if p in ballot])}


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
    projects = [project for b in profile if project in b]
    if projects:
        return int(project in ballot) * frac(project.cost, len(projects))
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
