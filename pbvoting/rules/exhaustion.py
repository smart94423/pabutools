from copy import deepcopy


def completion_by_rule_combination(instance, profile, rule_sequence):
    budget_allocation = []
    for rule in rule_sequence:
        budget_allocation += rule(instance, profile, initial_budget_allocation=budget_allocation)
        if instance.is_exhaustive(budget_allocation):
            break
    return budget_allocation


def exhaustion_by_budget_increase(rule, instance, profile, budget_step=1):
    current_instance = deepcopy(instance)
    previous_budget_allocation = []
    while True:
        budget_allocation = rule(current_instance, profile)
        if not instance.is_feasible(budget_allocation):
            return previous_budget_allocation
        if instance.is_exhaustive(budget_allocation):
            return budget_allocation
        current_instance.budget_limit += budget_step
        previous_budget_allocation = budget_allocation
