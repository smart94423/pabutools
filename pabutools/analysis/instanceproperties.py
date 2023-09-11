from pabutools.election.instance import Instance, total_cost

from numbers import Number

import numpy as np

from pabutools.fractions import frac


def sum_project_cost(instance: Instance) -> Number:
    """
    Returns the total cost of all the projects in the instance.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.

    Returns
    -------
        Number
            The total cost.

    """
    return total_cost(instance)


def funding_scarcity(instance: Instance) -> Number:
    """
    Returns the ratio of the total cost of the instance, divided by the budget limit. This measure is called the funding
    scarcity.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.

    Returns
    -------
        Number
            The funding scarcity of the instance.

    """
    if instance.budget_limit > 0:
        return frac(total_cost(instance), instance.budget_limit)
    raise ValueError(
        "funding scarcity can only be calculated for instances with budget limit > 0"
    )


def avg_project_cost(instance: Instance) -> Number:
    """
    Returns the average cost of a project.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.

    Returns
    -------
        Number
            The average cost of a project.

    """
    return frac(total_cost(instance), len(instance))


def median_project_cost(instance: Instance) -> Number:
    """
    Returns the median cost of a project.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.

    Returns
    -------
        Number
            The median cost of a project.

    """
    return float(np.median([project.cost for project in instance]))


def std_dev_project_cost(instance: Instance) -> Number:
    """
    Returns the standard deviation of the costs of the projects.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.

    Returns
    -------
        Number
            The standard deviation.

    """
    return float(np.std([project.cost for project in instance], dtype=np.float64))
