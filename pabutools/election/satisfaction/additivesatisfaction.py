from __future__ import annotations

from collections.abc import Callable, Iterable
from numbers import Number

from pabutools.election.satisfaction.satisfactionmeasure import SatisfactionMeasure
from pabutools.election.ballot import AbstractBallot, AbstractApprovalBallot, AbstractCardinalBallot
from pabutools.election.instance import Instance, Project, total_cost
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
        func: Callable[[Instance, AbstractProfile, AbstractBallot, Project, dict], Number],
    ) -> None:
        super(AdditiveSatisfaction, self).__init__(instance, profile, ballot)
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
    ballot: AbstractApprovalBallot,
    project: Project,
    precomputed_values: dict,
) -> int:
    """
    Computes the cardinality satisfaction for approval ballots. It is equal to 1 if the project is approved and 0
    otherwise.

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
        int
            The cardinality satisfaction.

    """
    return int(project in ballot)


class Cardinality_Sat(AdditiveSatisfaction):
    def __init__(self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot):
        super(Cardinality_Sat, self).__init__(
            instance, profile, ballot, cardinality_sat_func
        )


def relative_cardinality_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractApprovalBallot,
    project: Project,
    precomputed_values: dict,
) -> int:
    """
    Computes the relative cardinality satisfaction for approval ballots. If the project is approved then it is equal
    to 1 divided by the largest number of approved projects that can be selected in any budget allocation. If the
    project is not approved, or if the previous denominator is 0, then it is equal to 0.

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
        int
            The relative cardinality satisfaction.

    """
    if precomputed_values["max_budget_allocation_card"] == 0:
        return 0
    return frac(
        int(project in ballot), precomputed_values["max_budget_allocation_card"]
    )


class Relative_Cardinality_Sat(AdditiveSatisfaction):
    def __init__(self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot):
        super(Relative_Cardinality_Sat, self).__init__(
            instance, profile, ballot, relative_cardinality_sat_func
        )

    def preprocessing(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot
    ):
        ballot_sorted = sorted(ballot, key=lambda p: (p.cost))
        i, c = 0, 0
        while i < len(ballot) and c + ballot_sorted[i].cost <= instance.budget_limit:
            c += ballot_sorted[i].cost
            i += 1
        return {"max_budget_allocation_card": i}


def cost_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractApprovalBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    return int(project in ballot) * project.cost


class Cost_Sat(AdditiveSatisfaction):
    def __init__(self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot):
        super(Cost_Sat, self).__init__(instance, profile, ballot, cost_sat_func)


def relative_cost_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractApprovalBallot,
    project: Project,
    precomputed_values: dict,
) -> int:
    if precomputed_values["max_budget_allocation_cost"] == 0:
        return 0  # TODO
    return frac(
        int(project in ballot), precomputed_values["max_budget_allocation_cost"]
    )


class Relative_Cost_Sat(AdditiveSatisfaction):
    def __init__(self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot):
        super(Relative_Cost_Sat, self).__init__(
            instance, profile, ballot, relative_cost_sat_func
        )

    def preprocessing(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot
    ):
        return {"max_budget_allocation_cost": 1}


def relative_cost_non_normalised_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractApprovalBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    return frac(
        int(project in ballot) * project.cost, precomputed_values["total_ballot_cost"]
    )


class Relative_Cost_Non_Normalised_Sat(AdditiveSatisfaction):
    def __init__(self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot):
        super(Relative_Cost_Non_Normalised_Sat, self).__init__(
            instance, profile, ballot, relative_cost_non_normalised_sat_func
        )

    def preprocessing(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot
    ):
        return {"total_ballot_cost": total_cost([p for p in ballot if p in ballot])}


def effort_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractApprovalBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    projects = [project for b in profile if project in b]
    if projects:
        return int(project in ballot) * frac(project.cost, len(projects))
    return 0


class Effort_Sat(AdditiveSatisfaction):
    def __init__(self, instance: Instance, profile: AbstractProfile, ballot: AbstractApprovalBallot):
        super(Effort_Sat, self).__init__(instance, profile, ballot, effort_sat_func)


def additive_card_sat_func(
    instance: Instance,
    profile: AbstractProfile,
    ballot: AbstractCardinalBallot,
    project: Project,
    precomputed_values: dict,
) -> Number:
    return ballot.get(project, 0)


class Additive_Cardinal_Sat(AdditiveSatisfaction):
    def __init__(
        self, instance: Instance, profile: AbstractProfile, ballot: AbstractCardinalBallot
    ) -> None:
        super(Additive_Cardinal_Sat, self).__init__(
            instance, profile, ballot, additive_card_sat_func
        )
