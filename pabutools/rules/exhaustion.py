from copy import deepcopy, copy
from profile import Profile
from collections.abc import Iterable, Callable
from pabutools.election.instance import Instance, Project


def completion_by_rule_combination(
    instance: Instance,
    profile: Profile,
    rule_sequence: Iterable[Callable],
    rule_params: Iterable[dict] = None,
    initial_budget_allocation: Iterable[Project] = None,
) -> list[Project]:
    """
    Runs the given rules on the given instance and profile in sequence. This is useful if the first rules are
    non-exhaustive.
    Parameters. For now, only resolute rules are supported
    ----------
        instance : pabutools.instance.pbinstance.PBInstance
            The instance.
        profile : pabutools.instance.profile.Profile
            The profile.
        rule_sequence:
            Iterable of the rule functions
        rule_params (optional):
            Iterable of dictionaries of additional parameters that are passed to the rule functions
    Returns
    -------
        list of pabutools.instance.pbinstance.Project
    """
    if rule_params is not None and len(rule_sequence) != len(rule_params):
        raise ValueError(
            "Parameters rule_sequence and rule_params must be of equal length."
        )
    if rule_params is None:
        rule_params = [{} for _ in rule_sequence]
    if initial_budget_allocation is not None:
        budget_allocation = list(initial_budget_allocation)
    else:
        budget_allocation = []
    for index, rule in enumerate(rule_sequence):
        budget_allocation = rule(
            instance,
            profile,
            initial_budget_allocation=budget_allocation,
            **rule_params[index]
        )
        if instance.is_exhaustive(budget_allocation):
            break
    return budget_allocation


def exhaustion_by_budget_increase(
    instance: Instance,
    profile: Profile,
    rule: Callable,
    rule_params=None,
    initial_budget_allocation: Iterable[Project] = None,
    budget_step: int = 1,
) -> list[Project]:
    """
    Runs the given rule iteratively with increasing budget, until an exhaustive allocation is retreived or
    the budget limit is exceeded by the rule with increased budget.
    For now, only resolute rules are supported.
    ----------
        instance : pabutools.instance.pbinstance.PBInstance
            The instance.
        profile : pabutools.instance.profile.Profile
            The profile.
        rule:
            The rule function
        rule_params:
            A dictionary of additional parameters that are passed to the rule function
    Returns
    -------
        list of pabutools.instance.pbinstance.Project
    """
    if rule_params is None:
        rule_params = {}
    current_instance = deepcopy(instance)
    if initial_budget_allocation is not None:
        initial_budget_allocation = list(initial_budget_allocation)
        previous_budget_allocation = copy(initial_budget_allocation)
    else:
        previous_budget_allocation = []
        initial_budget_allocation = []
    rule_params["initial_budget_allocation"] = initial_budget_allocation
    while True:
        budget_allocation = rule(current_instance, profile, **rule_params)
        if not instance.is_feasible(budget_allocation):
            return previous_budget_allocation
        if instance.is_exhaustive(budget_allocation):
            return budget_allocation
        current_instance.budget_limit += budget_step
        previous_budget_allocation = budget_allocation
