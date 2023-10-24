from collections.abc import Iterable

from pabutools.analysis.cohesiveness import cohesive_groups
from pabutools.election import Instance, AbstractApprovalProfile, Project, SatisfactionMeasure, Additive_Cardinal_Sat, \
    AbstractCardinalProfile


def is_strong_EJR_approval(
        instance: Instance,
        profile: AbstractApprovalProfile,
        sat_class: type[SatisfactionMeasure],
        budget_allocation: Iterable[Project]
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        all_agents_sat = True
        for sat in profile.as_sat_profile(sat_class):
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
        budget_allocation: Iterable[Project]
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        one_agent_sat = False
        for sat in profile.as_sat_profile(sat_class):
            if sat.sat(budget_allocation) >= sat.sat(project_set):
                one_agent_sat = True
                break
        if not one_agent_sat:
            return False
    return True


def is_PJR_approval(
        instance: Instance,
        profile: AbstractApprovalProfile,
        sat_class: type[SatisfactionMeasure],
        budget_allocation: Iterable[Project]
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        threshold = sat_class(instance, profile, project_set).sat(project_set)
        group_approved = {p for p in budget_allocation if any(p in b for b in profile)}
        group_sat = sat_class(instance, profile, group_approved).sat(group_approved)
        if not group_sat < threshold:
            return False
    return True


def is_strong_EJR_cardinal(
        instance: Instance,
        profile: AbstractCardinalProfile,
        budget_allocation: Iterable[Project]
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        all_agents_sat = True
        threshold = sum(min(b[p] for b in profile) for p in project_set)
        for sat in profile.as_sat_profile(Additive_Cardinal_Sat):
            if sat.sat(budget_allocation) < threshold:
                all_agents_sat = False
                break
        if not all_agents_sat:
            return False
    return True


def is_EJR_cardinal(
        instance: Instance,
        profile: AbstractCardinalProfile,
        budget_allocation: Iterable[Project]
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        one_agent_sat = False
        threshold = sum(min(b[p] for b in profile) for p in project_set)
        for sat in profile.as_sat_profile(Additive_Cardinal_Sat):
            if sat.sat(budget_allocation) >= threshold:
                one_agent_sat = True
                break
        if not one_agent_sat:
            return False
    return True


def is_PJR_cardinal(
        instance: Instance,
        profile: AbstractCardinalProfile,
        budget_allocation: Iterable[Project]
) -> bool:
    for group, project_set in cohesive_groups(instance, profile):
        threshold = sum(min(b[p] for b in profile) for p in project_set)
        group_sat = sum(max(b[p] for b in profile) for p in budget_allocation)
        if group_sat < threshold:
            return False
    return True
