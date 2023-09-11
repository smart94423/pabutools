from pabutools.election.instance import Instance, total_cost

from numbers import Number

import numpy as np
from mip import Model, xsum, maximize, BINARY

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



def max_budget_allocation_cardinality(instance: Instance) -> int:
    """
    Returns the maximum number of projects that can be chosen with respect to the budget limit.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.

    Returns
    -------
        int
            The maximum number of projects that can be chosen with respect to the budget limit.

    """
    projects_sorted = sorted(instance, key=lambda proj: proj.cost)
    cost = 0
    selected = 0
    for p in projects_sorted:
        new_total_cost = p.cost + cost
        if new_total_cost > instance.budget_limit:
            break
        cost = new_total_cost
        selected += 1
    return selected


def max_budget_allocation_cost(instance: Instance) -> Number:
    """
    Returns the maximum cost that can be spent with respect to the budget limit. This number is different from the limit,
    since the costs of the projects might not add up to the limit exactly.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance.

    Returns
    -------
        int
            The maximum cost that can be spent with respect to the budget limit.

    """
    mip_model = Model()
    mip_model.verbose = 0
    p_vars = {
        p: mip_model.add_var(var_type=BINARY, name="x_{}".format(p)) for p in instance
    }
    if p_vars:
        mip_model.objective = maximize(xsum(p_vars[p] * p.cost for p in instance))
        mip_model += (
            xsum(p_vars[p] * p.cost for p in instance) <= instance.budget_limit
        )
        mip_model.optimize()
        max_cost = mip_model.objective.x
        return frac(max_cost)
    return 0