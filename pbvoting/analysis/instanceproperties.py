from pbvoting.election.instance import Instance, total_cost

from numbers import Number

import numpy as np


def sum_project_cost(instance: Instance) -> Number:
    """total cost of all projects of an instance"""
    return total_cost(instance)


def funding_scarcity(instance: Instance) -> Number:
    """ratio of total cost of all projects to the budget limit"""
    if instance.budget_limit > 0:
        return total_cost(instance) / instance.budget_limit
    raise ValueError(
        "funding scarcity can only be calculated for instances with budget limit > 0"
    )


def avg_project_cost(instance: Instance) -> Number:
    """average cost of all projects of an instance"""
    return total_cost(instance) / len(instance)


def median_project_cost(instance: Instance) -> Number:
    """median cost of all projects of an instance"""
    return np.median([project.cost for project in instance])


def std_dev_project_cost(instance: Instance) -> float:
    """standard deviation of project costs"""
    return np.std([project.cost for project in instance], dtype=np.float64)
