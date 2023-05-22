from copy import copy
from pbvoting.instance.pbinstance import total_cost


def remove_unwanted_projects(instance, profile):
    to_remove = copy(instance)
    for ballot in profile:
        for project in ballot:
            if project in to_remove:
                to_remove.remove(project)

    for project in to_remove:
        instance.remove(project)

    return instance


def completion_by_rule_resolute(primary_rule, secondary_rule, instance, profile):
    remove_unwanted_projects(instance, profile)

    allocation = primary_rule(instance, profile)
    if not instance.is_exhaustive(allocation):
        allocation += secondary_rule(instance, profile, allocation)
    return allocation


def completion_by_budget_increase(rule, instance, profile, budget_step=1):
    original_instance = copy(instance)
    remove_unwanted_projects(original_instance, profile)

    allocation = rule(original_instance, profile)

    if original_instance.is_exhaustive(allocation) or len(allocation) == len(original_instance):
        return allocation

    current_instance = copy(original_instance)
    while True:
        current_instance.budget_limit += budget_step

        previous_allocation = allocation
        allocation = rule(current_instance, profile)

        if not original_instance.is_feasible(allocation):
            return previous_allocation
        if original_instance.is_exhaustive(allocation):
            return allocation
