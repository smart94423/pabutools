from pbvoting.instance.pbinstance import *
from pbvoting.instance.profile import *
import numpy as np
from pbvoting.fractions import number_as_frac


def sum_project_cost(instance: PBInstance) -> Fraction:
    """total cost of all projects of an instance"""
    return np.sum([project.cost for project in instance])


def funding_scarcity(instance: PBInstance) -> Fraction:
    """ratio of total cost of all projects to the budget limit"""
    return sum_project_cost(instance) / instance.budget_limit


def avg_project_cost(instance: PBInstance) -> Fraction:
    """average cost of all projects of an instance"""
    return sum_project_cost(instance) / len(instance)


def median_project_cost(instance: PBInstance) -> Fraction:
    """median cost of all projects of an instance"""
    return np.median([project.cost for project in instance])


def std_dev_project_cost(instance: PBInstance) -> float:
    """standard deviation of project costs"""    
    return np.std([project.cost for project in instance], dtype=np.float64)