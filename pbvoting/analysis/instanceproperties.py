from pbvoting.election.instance import *
from pbvoting.election.profile import *
import numpy as np
from pbvoting.fractions import number_as_frac


def sum_project_cost(instance: Instance) -> Fraction:
    """total cost of all projects of an instance"""
    return np.sum([project.cost for project in instance])


def funding_scarcity(instance: Instance) -> Fraction:
    """ratio of total cost of all projects to the budget limit"""
    if instance.budget_limit > 0:
        return sum_project_cost(instance) / instance.budget_limit
    raise ValueError("funding scarcity can only be calculated for projects with budget limit > 0")

def avg_project_cost(instance: Instance) -> Fraction:
    """average cost of all projects of an instance"""
    return sum_project_cost(instance) / len(instance)


def median_project_cost(instance: Instance) -> Fraction:
    """median cost of all projects of an instance"""
    return np.median([project.cost for project in instance])


def std_dev_project_cost(instance: Instance) -> float:
    """standard deviation of project costs"""    
    return np.std([project.cost for project in instance], dtype=np.float64)