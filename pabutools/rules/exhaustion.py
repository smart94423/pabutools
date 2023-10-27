from __future__ import annotations

from copy import deepcopy, copy
from collections.abc import Collection, Callable, Iterable, Sequence

from pabutools.election.instance import Instance, Project
from pabutools.election.profile import AbstractProfile
from pabutools.fractions import frac

from pabutools.utils import Numeric


def completion_by_rule_combination(
    instance: Instance,
    profile: AbstractProfile,
    rule_sequence: Sequence[Callable],
    rule_params: Sequence[dict] | None = None,
    initial_budget_allocation: Collection[Project] | None = None,
    resoluteness: bool = True,
) -> Collection[Project] | Iterable[Collection[Project]]:
    """
    Runs the given rules on the given instance and profile in sequence until an exhaustive budget allocation has been
    reached (or all rules have been applied). This is useful if the first rules are non-exhaustive.
    In the irresolute version, all outcomes are completed separately.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        rule_sequence: Iterable[Callable]
            Iterable of the rule functions.
        rule_params: Iterable[dict], optional
            Iterable of dictionaries of additional parameters that are passed as keyword arguments to the rule
            functions. Defaults to `{}`.
        initial_budget_allocation : Iterable[:py:class:`~pabutools.election.instance.Project`], optional
            An initial budget allocation, typically empty. Defaults to `[]`.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.

    Returns
    -------
        Collection[Project] | Iterable[Collection[Project]]
            The selected projects.
    """
    if rule_params is not None and len(rule_sequence) != len(rule_params):
        raise ValueError(
            "Parameters rule_sequence and rule_params must be of equal length."
        )
    if rule_params is None:
        rule_params = [{} for _ in rule_sequence]
    for i, params in enumerate(rule_params):
        if "resoluteness" in params and params["resoluteness"] != resoluteness:
            raise ValueError(
                f"The rule parameter at position {i} sets the resoluteness parameter to a different "
                "one that the resoluteness argument passed to completion_by_rule_combination."
            )
    budget_allocations = []
    res = []
    if initial_budget_allocation is not None:
        budget_allocations.append(list(initial_budget_allocation))
    else:
        budget_allocations.append([])
    for index, rule in enumerate(rule_sequence):
        new_budget_allocations = []
        for budget_allocation in budget_allocations:
            outcome = rule(
                instance,
                profile,
                initial_budget_allocation=budget_allocation,
                resoluteness=resoluteness,
                **rule_params[index],
            )
            if resoluteness:
                if instance.is_exhaustive(outcome):
                    return outcome
                else:
                    new_budget_allocations = [outcome]
            else:
                all_resolute = True
                for alloc in outcome:
                    if instance.is_exhaustive(alloc):
                        if alloc not in res:
                            res.append(alloc)
                    else:
                        all_resolute = False
                        new_budget_allocations.append(alloc)
                if all_resolute:
                    return res
        budget_allocations = new_budget_allocations
    if resoluteness:
        return budget_allocations[0]
    return res + budget_allocations


def exhaustion_by_budget_increase(
    instance: Instance,
    profile: AbstractProfile,
    rule: Callable,
    rule_params: dict | None = None,
    initial_budget_allocation: Collection[Project] | None = None,
    resoluteness: bool = True,
    budget_step: Numeric | None = None,
    budget_bound: Numeric | None = None,
) -> Collection[Project]:
    """
    Runs the given rule iteratively with increasing budget, until an exhaustive allocation is retrieved or
    the budget limit is exceeded by the rule with increased budget. In the irresolute version, as soon as one outcome is
    exhaustive or infeasible, the procedure stops.

    Parameters
    ----------
        instance: :py:class:`~pabutools.election.instance.Instance`
            The instance.
        profile : :py:class:`~pabutools.election.profile.profile.AbstractProfile`
            The profile.
        rule:
            The rule function
        rule_params: dict, optional
            Dictionary of additional parameters that are passed as keyword arguments to the rule
            function. Defaults to `{}`.
        initial_budget_allocation: Collection[Project], optional
            An initial budget allocation, typically empty. Defaults to `[]`. Overrides the parameter in `rule_params`.
        resoluteness : bool, optional
            Set to `False` to obtain an irresolute outcome, where all tied budget allocations are returned.
            Defaults to True.
        budget_step: Numeric
            The step at which the budget is increased. Defaults to 1% of the budget limit.
        budget_bound: Numeric
            An upper bound on the budget limit. The method stops if this bound is exceeded. Defaults to the budget limit
            multiplied by the number of agents plus 1.

    Returns
    -------
        Collection[Project]
            The selected projects.
    """
    if rule_params is None:
        rule_params = {}
    current_instance = deepcopy(instance)
    if initial_budget_allocation is None:
        initial_budget_allocation = []
    else:
        initial_budget_allocation = list(initial_budget_allocation)
    rule_params["initial_budget_allocation"] = initial_budget_allocation
    if resoluteness:
        previous_outcome = copy(initial_budget_allocation)
    else:
        previous_outcome = [copy(initial_budget_allocation)]
    if budget_step is None:
        budget_step = instance.budget_limit * frac(1, 100)
    if budget_bound is None:
        budget_bound = instance.budget_limit * (profile.num_ballots() + 1)
    rule_params["resoluteness"] = resoluteness
    while current_instance.budget_limit <= budget_bound:
        outcome = rule(current_instance, profile, **rule_params)
        if resoluteness:
            if not instance.is_feasible(outcome):
                return previous_outcome
            if instance.is_exhaustive(outcome):
                return outcome
            current_instance.budget_limit += budget_step
            previous_outcome = outcome
        else:
            if any(not instance.is_feasible(o) for o in outcome):
                return previous_outcome
            if any(instance.is_exhaustive(o) for o in outcome):
                return outcome
            current_instance.budget_limit += budget_step
            previous_outcome = outcome
    return previous_outcome
