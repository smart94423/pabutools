from copy import deepcopy
from profile import Profile
from collections.abc import Iterable, Callable
from pbvoting.instance.pbinstance import PBInstance, Project


def completion_by_rule_combination(instance: PBInstance,
                                   profile: Profile,
                                   rule_sequence: Iterable[Callable],
                                   rule_params: Iterable[dict] = None,
                                   initial_budget_allocation: Iterable[Project] = None,
                                   ) -> list[Project]:
    """
        Runs the given rules on the given instance and profile in sequence. This is useful if the first rules are non-exhaustive.
        Parameters. For now, only resolute rules are supported 
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            rule_sequence:
                Iterable of the rule functions  
            rule_params (optional):
                Iterable of dictionaries of additional parameters that are passed to the rule functions
        Returns
        -------
            list of pbvoting.instance.pbinstance.Project
    """
    if rule_params != None and len(rule_sequence) != len(rule_params):
        raise Exception("rule_sequence and rule_params must be of equal length.")
    if rule_params == None:
        rule_params = [{} for i in range(len(rule_sequence))]
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []
    for index, rule in enumerate(rule_sequence):
        budget_allocation += rule(instance, profile, initial_budget_allocation=budget_allocation, **rule_params[index])
        if instance.is_exhaustive(budget_allocation):
            break
    return budget_allocation


def exhaustion_by_budget_increase(instance: PBInstance,
                                  profile: Profile,
                                  rule: Callable,
                                  rule_params: dict = {},
                                  initial_budget_allocation: Iterable[Project] = None,
                                  budget_step: int = 1
                                  ) -> list[Project]:
    """
        Runs the given rule iteratively with increasing budget, until an exhaustive allocation is retreived or
        the budget limit is exceeded by the rule with increased budget.
        For now, only resolute rules are supported.
        ----------
            instance : pbvoting.instance.pbinstance.PBInstance
                The instance.
            profile : pbvoting.instance.profile.Profile
                The profile.
            rule:
                The rule function
            rule_params:
                A dictionary of additional parameters that are passed to the rule function 
        Returns
        -------
            list of pbvoting.instance.pbinstance.Project
    """
    current_instance = deepcopy(instance)
    if initial_budget_allocation is not None:
        previous_budget_allocation = list(initial_budget_allocation)
    else:
        previous_budget_allocation = []
    while True:
        budget_allocation = rule(current_instance, profile, **rule_params)
        if not instance.is_feasible(budget_allocation):
            return previous_budget_allocation
        if instance.is_exhaustive(budget_allocation):
            return budget_allocation
        current_instance.budget_limit += budget_step
        previous_budget_allocation = budget_allocation
