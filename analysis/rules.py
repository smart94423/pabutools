from pabutools.election import Cost_Sat, total_cost, Cardinality_Sat
from pabutools.rules import (
    greedy_utilitarian_welfare,
    sequential_phragmen,
    method_of_equal_shares,
    completion_by_rule_combination,
    exhaustion_by_budget_increase,
)
from pabutools.rules.maxwelfare import max_additive_utilitarian_welfare


def greed_cost_res(instance, profile):
    return greedy_utilitarian_welfare(
        instance, profile, sat_class=Cost_Sat, resoluteness=True
    )


def maxwelfare_cost_res(instance, profile):
    return max_additive_utilitarian_welfare(
        instance, profile, sat_class=Cost_Sat, resoluteness=True
    )


def greed_card_res(instance, profile):
    return greedy_utilitarian_welfare(
        instance, profile, sat_class=Cardinality_Sat, resoluteness=True
    )


def seqphragmen_res(instance, profile):
    return sequential_phragmen(instance, profile, resoluteness=True)


def mes_cost_res(instance, profile):
    return method_of_equal_shares(
        instance, profile, sat_class=Cost_Sat, resoluteness=True
    )


def mes_card_res(instance, profile):
    return method_of_equal_shares(
        instance, profile, sat_class=Cardinality_Sat, resoluteness=True
    )


def mes_cost_res_ex(instance, profile):
    return completion_by_rule_combination(
        instance,
        profile,
        [exhaustion_by_budget_increase, greedy_utilitarian_welfare],
        [
            {
                "rule": method_of_equal_shares,
                "budget_step": int(total_cost(instance) / 100),
                "rule_params": {"sat_class": Cost_Sat},
            },
            {"sat_class": Cost_Sat},
        ],
    )


def mes_card_res_ex(instance, profile):
    return completion_by_rule_combination(
        instance,
        profile,
        [exhaustion_by_budget_increase, greedy_utilitarian_welfare],
        [
            {
                "rule": method_of_equal_shares,
                "budget_step": int(total_cost(instance) / 100),
                "rule_params": {"sat_class": Cardinality_Sat},
            },
            {"sat_class": Cardinality_Sat},
        ],
    )


def all_approved_projects(instance, profile):
    res = set()
    for ballot in profile:
        res.update(ballot)
    return res
