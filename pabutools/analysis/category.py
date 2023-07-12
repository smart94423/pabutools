from collections.abc import Iterable

import numpy as np
from pabutools.election.instance import Instance, Project
from pabutools.election.profile import ApprovalProfile


def category_proportionality(
    instance: Instance,
    profile: ApprovalProfile,
    budget_allocation: Iterable[Project],
) -> float:
    categories = list(instance.categories)
    if len(categories) == 0:
        raise ValueError(
            "Category proportionality can only be computed for instances with categories."
        )
    if len(budget_allocation) == 0:
        return 0

    proportional_allocated_cost_per_category = {
        category: 0.0 for category in categories
    }
    allocated_cost_per_category = {category: 0.0 for category in categories}
    allocated_total_cost = 0.0
    for project in budget_allocation:
        allocated_total_cost += project.cost
        for category in project.categories:
            allocated_cost_per_category[category] += project.cost
    for category in categories:
        proportional_allocated_cost_per_category[category] = (
            allocated_cost_per_category[category] / allocated_total_cost
        )

    proportional_app_cost_per_category = {category: 0.0 for category in categories}
    for ballot in profile:
        app_cost_per_category = {category: 0.0 for category in categories}
        app_total_cost = 0.0
        for project in ballot:
            app_total_cost += project.cost
            for category in project.categories:
                app_cost_per_category[category] += project.cost
        for category in categories:
            proportional_app_cost_per_category[category] += (
                app_cost_per_category[category] / app_total_cost
            )
    for category in categories:
        proportional_app_cost_per_category[category] /= len(profile)

    mean_square_diff = 0.0
    for category in categories:
        mean_square_diff += (
            proportional_allocated_cost_per_category[category]
            - proportional_app_cost_per_category[category]
        ) ** 2
    mean_square_diff /= len(categories)

    return np.exp(-float(mean_square_diff))
