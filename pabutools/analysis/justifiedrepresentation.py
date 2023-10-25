from __future__ import annotations

from collections.abc import Collection, Callable, Iterable

from pabutools.utils import Numeric

from pabutools.analysis.cohesiveness import cohesive_groups, is_large_enough
from pabutools.election import (
    Instance,
    AbstractApprovalProfile,
    Project,
    SatisfactionMeasure,
    Additive_Cardinal_Sat,
    AbstractCardinalProfile,
    ApprovalBallot,
    total_cost,
)
from pabutools.utils import powerset


def is_in_core_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
) -> bool:
    for group in powerset(profile):
        if len(group) > 0:
            for proj_set in powerset(instance):
                if is_large_enough(
                    len(group),
                    profile.num_ballots(),
                    total_cost(proj_set),
                    instance.budget_limit,
                ):
                    all_better_alone = True
                    for ballot in group:
                        sat = sat_class(instance, profile, ballot)
                        if sat.sat(budget_allocation) >= sat.sat(proj_set):
                            all_better_alone = False
                            break
                    if all_better_alone:
                        return False
    return True


def is_strong_EJR_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        all_agents_sat = True
        for ballot in group:
            sat = sat_class(instance, profile, ballot)
            if sat.sat(budget_allocation) < sat.sat(project_set):
                all_agents_sat = False
                break
        if not all_agents_sat:
            return False
    return True


def is_EJR_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
    up_to_func: Callable[[Iterable[Numeric]], Numeric] | None = None,
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        one_agent_sat = False
        for ballot in group:
            sat = sat_class(instance, profile, ballot)
            surplus = 0
            if up_to_func is not None:
                surplus = up_to_func(
                    sat.sat_project(p)
                    for p in project_set
                    if p not in budget_allocation
                )
            if sat.sat(budget_allocation) + surplus >= sat.sat(project_set):
                one_agent_sat = True
                break
        if not one_agent_sat:
            return False
    return True


def is_EJR_any_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
) -> bool:
    return is_EJR_approval(
        instance,
        profile,
        sat_class,
        budget_allocation,
        up_to_func=lambda x: min(x, default=0),
    )


def is_EJR_one_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
) -> bool:
    return is_EJR_approval(
        instance,
        profile,
        sat_class,
        budget_allocation,
        up_to_func=lambda x: max(x, default=0),
    )


def is_PJR_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
    up_to_func: Callable[[Iterable[Numeric]], Numeric] | None = None,
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        sat = sat_class(instance, profile, ApprovalBallot(instance))
        threshold = sat.sat(project_set)
        group_approved = {p for p in budget_allocation if any(p in b for b in profile)}
        surplus = 0
        if up_to_func is not None:
            surplus = up_to_func(
                sat.sat_project(p) for p in project_set if p not in budget_allocation
            )
        group_sat = sat.sat(group_approved) + surplus
        if group_sat < threshold:
            return False
    return True


def is_PJR_any_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
) -> bool:
    return is_PJR_approval(
        instance,
        profile,
        sat_class,
        budget_allocation,
        up_to_func=lambda x: min(x, default=0),
    )


def is_PJR_one_approval(
    instance: Instance,
    profile: AbstractApprovalProfile,
    sat_class: type[SatisfactionMeasure],
    budget_allocation: Collection[Project],
) -> bool:
    return is_PJR_approval(
        instance,
        profile,
        sat_class,
        budget_allocation,
        up_to_func=lambda x: max(x, default=0),
    )


def is_strong_EJR_cardinal(
    instance: Instance,
    profile: AbstractCardinalProfile,
    budget_allocation: Collection[Project],
    sat_class: type[SatisfactionMeasure] = Additive_Cardinal_Sat,
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        all_agents_sat = True
        threshold = sum(min(b[p] for b in profile) for p in project_set)
        for ballot in group:
            sat = sat_class(instance, profile, ballot)
            if sat.sat(budget_allocation) < threshold:
                all_agents_sat = False
                break
        if not all_agents_sat:
            return False
    return True


def is_EJR_cardinal(
    instance: Instance,
    profile: AbstractCardinalProfile,
    budget_allocation: Collection[Project],
    sat_class: type[SatisfactionMeasure] = Additive_Cardinal_Sat,
    up_to_func: Callable[[Iterable[Numeric]], Numeric] | None = None,
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        one_agent_sat = False
        threshold = sum(min(b[p] for b in profile) for p in project_set)
        for ballot in group:
            sat = sat_class(instance, profile, ballot)
            surplus = 0
            if up_to_func is not None:
                surplus = up_to_func(
                    sat.sat_project(p)
                    for p in project_set
                    if p not in budget_allocation
                )
            if sat.sat(budget_allocation) + surplus >= threshold:
                one_agent_sat = True
                break
        if not one_agent_sat:
            return False
    return True


def is_EJR_one_cardinal(
    instance: Instance,
    profile: AbstractCardinalProfile,
    budget_allocation: Collection[Project],
) -> bool:
    return is_EJR_cardinal(
        instance, profile, budget_allocation, up_to_func=lambda x: min(x, default=0)
    )


def is_EJR_any_cardinal(
    instance: Instance,
    profile: AbstractCardinalProfile,
    budget_allocation: Collection[Project],
) -> bool:
    return is_EJR_cardinal(
        instance, profile, budget_allocation, up_to_func=lambda x: max(x, default=0)
    )


def is_PJR_cardinal(
    instance: Instance,
    profile: AbstractCardinalProfile,
    budget_allocation: Iterable[Project],
    up_to_func: Callable[[Iterable[Numeric]], Numeric] | None = None,
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        threshold = sum(min(b[p] for b in profile) for p in project_set)
        group_sat = sum(max(b[p] for b in profile) for p in budget_allocation)
        surplus = 0
        if up_to_func is not None:
            surplus = up_to_func(
                max(b[p] for b in profile)
                for p in project_set
                if p not in budget_allocation
            )
        if group_sat + surplus < threshold:
            return False
    return True


def is_PJR_any_cardinal(
    instance: Instance,
    profile: AbstractCardinalProfile,
    budget_allocation: Iterable[Project],
) -> bool:
    return is_PJR_cardinal(
        instance, profile, budget_allocation, up_to_func=lambda x: min(x, default=0)
    )


def is_PJR_one_cardinal(
    instance: Instance,
    profile: AbstractCardinalProfile,
    budget_allocation: Iterable[Project],
) -> bool:
    return is_PJR_cardinal(
        instance, profile, budget_allocation, up_to_func=lambda x: max(x, default=0)
    )
