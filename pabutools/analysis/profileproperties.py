import numpy as np

from numbers import Number

from pabutools.election import (
    AbstractApprovalProfile,
    AbstractCardinalProfile,
    AbstractProfile,
)
from pabutools.election import Instance, total_cost

from pabutools.fractions import frac
from pabutools.utils import mean_generator


def avg_ballot_length(instance: Instance, profile: AbstractProfile) -> Number:
    """
    Returns the average length of the ballots in the profile.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.

    Returns
    -------
        Number
            The average length of the ballots in the profile.

    """
    return mean_generator(
        len(ballot) * profile.multiplicity(ballot) for ballot in profile
    )


def median_ballot_length(instance: Instance, profile: AbstractProfile) -> int:
    """
    Returns the median length of the ballots in the profile.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.

    Returns
    -------
        Number
            The median length of the ballots in the profile.

    """
    return int(
        np.median([len(ballot) * profile.multiplicity(ballot) for ballot in profile])
    )


def avg_ballot_cost(instance: Instance, profile: AbstractProfile) -> Number:
    """
    Returns the average cost of the ballots in the profile.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.

    Returns
    -------
        Number
            The average cost of the ballots in the profile.

    """
    return mean_generator(
        total_cost(ballot) * profile.multiplicity(ballot) for ballot in profile
    )


def median_ballot_cost(instance: Instance, profile: AbstractProfile) -> Number:
    """
    Returns the median cost of the ballots in the profile.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.

    Returns
    -------
        Number
            The median cost of the ballots in the profile.

    """
    return float(
        np.median(
            [total_cost(ballot) * profile.multiplicity(ballot) for ballot in profile]
        )
    )


def avg_approval_score(instance: Instance, profile: AbstractApprovalProfile) -> Number:
    """
    Returns the average approval score of projects.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.approvalprofile.AbstractApprovalProfile`
            The profile.

    Returns
    -------
        Number
            The average approval score of projects.

    """
    return mean_generator([profile.approval_score(project) for project in instance])


def median_approval_score(
    instance: Instance, profile: AbstractApprovalProfile
) -> Number:
    """
    Returns the median approval score of projects.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.approvalprofile.AbstractApprovalProfile`
            The profile.

    Returns
    -------
        Number
            The median approval score of projects.

    """
    return float(
        np.median([frac(profile.approval_score(project)) for project in instance])
    )


def avg_total_score(instance: Instance, profile: AbstractCardinalProfile) -> Number:
    """
    Returns the average score assigned to a project by the voters.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.cardinalprofile.AbstractCardinalProfile`
            The profile.

    Returns
    -------
        Number
            The average score assigned to a project.

    """
    return mean_generator(profile.total_score(project) for project in instance)


def median_total_score(instance: Instance, profile: AbstractCardinalProfile) -> Number:
    """
    Returns the median score assigned to a project by the voters.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.cardinalprofile.AbstractCardinalProfile`
            The profile.

    Returns
    -------
        Number
            The median score assigned to a project.

    """
    return float(
        np.median([frac(profile.total_score(project)) for project in instance])
    )
