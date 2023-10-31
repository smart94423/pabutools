import sys
import os

from pabutools.rules.mes import naive_mes

pabutools_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, pabutools_path)

from pabutools.election import (
    parse_pabulib,
    Cost_Sat,
    Instance,
    Project,
    ApprovalProfile,
    ApprovalBallot,
    Cardinality_Sat,
)
from pabutools.rules import method_of_equal_shares, exhaustion_by_budget_increase

import pabutools.fractions

from pabutools.fractions import frac


def equal_shares_fast(instance, profile, sat_class):
    projects = set(instance)
    costs = {p: p.cost for p in projects}
    sat_profile = profile.as_sat_profile(sat_class)
    utilities = [
        {p: sat.sat_project(p) for p in instance} for i, sat in enumerate(sat_profile)
    ]
    voters = range(len(utilities))
    approvers = {
        p: [i for i, sat in enumerate(sat_profile) if p in sat.ballot] for p in instance
    }
    total_utils = {p: sat_profile.total_satisfaction_project(p) for p in instance}
    return equal_shares_fixed_budget(
        voters,
        projects,
        costs,
        utilities,
        total_utils,
        approvers,
        instance.budget_limit,
    )


def equal_shares_iterated_fast(instance, profile, sat_class):
    projects = set(instance)
    costs = {p: p.cost for p in projects}
    sat_profile = profile.as_sat_profile(sat_class)
    utilities = [
        {p: sat.sat_project(p) for p in instance} for i, sat in enumerate(sat_profile)
    ]
    voters = range(len(utilities))
    return equal_shares(voters, projects, costs, utilities, instance.budget_limit)


def equal_shares_iterated_fast_approval(instance, profile, budget_multiplier=1):
    projects = set(instance)
    costs = {p: p.cost for p in projects}
    voters = range(len(profile))
    approvers = {p: [i for i in voters if p in profile[i]] for p in instance}
    return equal_shares_approval(
        voters, projects, costs, approvers, instance.budget_limit, budget_multiplier
    )


def equal_shares_fast_approval(instance, profile):
    projects = set(instance)
    costs = {p: p.cost for p in projects}
    voters = range(len(profile))
    approvers = {p: [i for i in voters if p in profile[i]] for p in instance}
    return equal_shares_fixed_budget_approval(
        voters, projects, costs, approvers, instance.budget_limit
    )


def equal_shares_fixed_budget(
    N, C, cost, util, total_utility, approvers, B, verbose=False
):
    def break_ties(N, C, cost, approvers, choices):
        min_proj = None
        for p in choices:
            if min_proj is None or p.name < min_proj:
                min_proj = p
        return [min_proj]

    budget = {i: frac(B, len(N)) for i in N}
    remaining = {}  # remaining candidate -> previous effective vote count
    for c in C:
        if cost[c] > 0 and len(approvers[c]) > 0:
            remaining[c] = total_utility[c]
    if verbose:
        tmp = sorted([(p, a) for p, a in remaining.items()], key=lambda x: x[1])
        for p, a in tmp:
            print(f"{p} -- {float(a)}")
    winners = []
    while True:
        best = []
        best_eff_vote_count = 0
        # go through remaining candidates in order of decreasing previous effective vote count
        remaining_sorted = sorted(remaining, key=lambda c: remaining[c], reverse=True)
        if verbose:
            print("========================")
        for c in remaining_sorted:
            if verbose:
                print(f"\tConsidering: {c}")
            previous_eff_vote_count = remaining[c]
            if previous_eff_vote_count < best_eff_vote_count:
                # c cannot be better than the best so far
                break
            money_behind_now = sum(budget[i] for i in approvers[c])
            if money_behind_now < cost[c]:
                # c is not affordable
                del remaining[c]
                continue
            # calculate the effective vote count of c
            approvers[c].sort(key=lambda i: frac(budget[i], util[i][c]))
            paid_so_far = 0
            denominator = total_utility[c]
            for i in approvers[c]:
                # compute payment if remaining approvers pay proportional to their utility
                payment_factor = frac(cost[c] - paid_so_far, denominator)
                eff_vote_count = frac(cost[c], payment_factor)
                if payment_factor * util[i][c] > budget[i]:
                    # i cannot afford the payment, so pays entire remaining budget
                    paid_so_far += budget[i]
                    denominator -= util[i][c]
                else:
                    # i (and all later approvers) can afford the payment; stop here
                    if verbose:
                        print(
                            f"\t\tFactor: {float(payment_factor)} = ({cost[c]} - {paid_so_far})/{denominator}"
                        )
                        print(f"\t\tEff: {float(eff_vote_count)}")
                    remaining[c] = eff_vote_count
                    if eff_vote_count > best_eff_vote_count:
                        best_eff_vote_count = eff_vote_count
                        best = [c]
                    elif eff_vote_count == best_eff_vote_count:
                        best.append(c)
                    break
        if not best:
            # no remaining candidates are affordable
            break
        best = break_ties(N, C, cost, total_utility, best)
        if len(best) > 1:
            raise Exception(
                "Tie-breaking failed: tie between projects "
                + ", ".join(best)
                + "could not be resolved. Another tie-breaking needs to be added."
            )
        best = best[0]
        winners.append(best)
        del remaining[best]
        # charge the approvers of best
        payment_factor = frac(cost[best], best_eff_vote_count)
        for i in approvers[best]:
            payment = payment_factor * util[i][best]
            if budget[i] > payment:
                budget[i] -= payment
            else:
                budget[i] = 0
    return winners


def equal_shares(N, C, cost, u, B):
    approvers = {c: [i for i in N if u[i][c] > 0] for c in C}
    total_utility = {c: sum(u[i][c] for i in N) for c in C}
    mes = equal_shares_fixed_budget(N, C, cost, u, total_utility, approvers, B)
    # add1 completion
    # start with integral per-voter budget
    budget = frac(B, len(N)) * len(N)
    current_cost = sum(cost[c] for c in mes)
    while True:
        # is current outcome exhaustive?
        is_exhaustive = True
        for extra in C:
            if extra not in mes and current_cost + cost[extra] <= B:
                is_exhaustive = False
                break
        # if so, stop
        if is_exhaustive:
            break
        # would the next highest budget work?
        next_budget = budget + len(N)
        next_mes = equal_shares_fixed_budget(
            N, C, cost, u, total_utility, approvers, next_budget, verbose=False
        )
        # print(f"Next: {next_mes}")
        current_cost = sum(cost[c] for c in next_mes)
        if current_cost <= B:
            # yes, so continue with that budget
            budget = next_budget
            mes = next_mes
        else:
            # no, so stop
            break
    return mes


def equal_shares_approval(N, C, cost, approvers, B, budget_multiplier=1):
    mes = equal_shares_fixed_budget_approval(N, C, cost, approvers, B)
    # add1 completion
    # start with integral per-voter budget
    budget = frac(B, len(N)) * len(N)
    current_cost = sum(cost[c] for c in mes)
    while True:
        # is current outcome exhaustive?
        is_exhaustive = True
        for extra in C:
            if extra not in mes and current_cost + cost[extra] <= B:
                is_exhaustive = False
                break
        # if so, stop
        if is_exhaustive:
            break
        # would the next highest budget work?
        next_budget = budget + len(N) * budget_multiplier
        next_mes = equal_shares_fixed_budget_approval(
            N, C, cost, approvers, next_budget, verbose=False
        )
        current_cost = sum(cost[c] for c in next_mes)
        if current_cost <= B:
            # yes, so continue with that budget
            budget = next_budget
            mes = next_mes
        else:
            # no, so stop
            break
    return mes


def equal_shares_fixed_budget_approval(N, C, cost, approvers, B, verbose=False):
    def break_ties(N, C, cost, approvers, choices):
        min_proj = None
        for p in choices:
            if min_proj is None or p.name < min_proj:
                min_proj = p
        # if len(choices) > 1:
        #     print(f"Breaking!! {choices} -- {min_proj}")
        return [min_proj]

    budget = {i: frac(B, len(N)) for i in N}
    remaining = {}  # remaining candidate -> previous effective vote count
    for c in C:
        if cost[c] > 0 and len(approvers[c]) > 0:
            remaining[c] = len(approvers[c])
    if verbose:
        tmp = sorted([(p, a) for p, a in remaining.items()], key=lambda x: -x[1])
        for p, a in tmp:
            print(f"{p} -- {float(a)}")
    winners = []
    while True:
        best = []
        best_eff_vote_count = 0
        # go through remaining candidates in order of decreasing previous effective vote count
        remaining_sorted = sorted(remaining, key=lambda c: remaining[c], reverse=True)
        if verbose:
            print("========================")
            tmp = sorted([(p, a) for p, a in remaining.items()], key=lambda x: -x[1])
            for p, a in tmp[:5]:
                print(f"{p} -- {float(a)}")
        for c in remaining_sorted:
            if verbose:
                print(f"\tConsidering: {c}")
            previous_eff_vote_count = remaining[c]
            if previous_eff_vote_count < best_eff_vote_count:
                # c cannot be better than the best so far
                break
            money_behind_now = sum(budget[i] for i in approvers[c])
            if money_behind_now < cost[c]:
                # c is not affordable
                del remaining[c]
                continue
            # calculate the effective vote count of c
            approvers[c].sort(key=lambda i: budget[i])
            paid_so_far = 0
            denominator = len(approvers[c])
            for i in approvers[c]:
                # compute payment if remaining approvers pay equally
                max_payment = frac(cost[c] - paid_so_far, denominator)
                eff_vote_count = frac(cost[c], max_payment)
                if max_payment > budget[i]:
                    # i cannot afford the payment, so pays entire remaining budget
                    paid_so_far += budget[i]
                    denominator -= 1
                else:
                    # i (and all later approvers) can afford the payment; stop here
                    if verbose:
                        print(
                            f"\t\tFactor: {float(max_payment)} = ({cost[c]} - {paid_so_far})/{denominator}"
                        )
                        print(f"\t\tEff: {float(eff_vote_count)}")
                    remaining[c] = eff_vote_count
                    if eff_vote_count > best_eff_vote_count:
                        best_eff_vote_count = eff_vote_count
                        best = [c]
                    elif eff_vote_count == best_eff_vote_count:
                        best.append(c)
                    break
        if not best:
            # no remaining candidates are affordable
            break
        if verbose:
            print(best)
        best = break_ties(N, C, cost, approvers, best)
        if len(best) > 1:
            raise Exception(
                "Tie-breaking failed: tie between projects "
                + ", ".join(best)
                + "could not be resolved. Another tie-breaking needs to be added."
            )
        best = best[0]
        winners.append(best)
        del remaining[best]
        # charge the approvers of best
        best_max_payment = frac(cost[best], best_eff_vote_count)
        for i in approvers[best]:
            if budget[i] > best_max_payment:
                budget[i] -= best_max_payment
            else:
                budget[i] = 0
    return winners


if __name__ == "__main__":
    pabutools.fractions.FRACTION = "float"
    instance, profile = parse_pabulib("poland_wieliczka_2023.pb")
    # instance, profile = parse_pabulib("poland_warszawa_2019_ursynow.pb")
    # profile = profile.as_multiprofile()

    # instance = Instance([Project("1", 2), Project("2", 3), Project("3", 3)], budget_limit=4)
    # profile = ApprovalProfile([ApprovalBallot([instance.get_project("1")]), ApprovalBallot([instance.get_project("2")]), ApprovalBallot([instance.get_project("3")]), ApprovalBallot([instance.get_project("3")])])

    # winners_fast = equal_shares_fast(instance, profile, sat_class=Cardinality_Sat)
    # winners_fast = equal_shares_iterated_fast(
    #     instance, profile, sat_class=Cardinality_Sat
    # )
    # print(len(winners_fast))
    # print(winners_fast)
    # winners_fast = equal_shares_fast_approval(instance, profile)
    winners_fast = equal_shares_iterated_fast_approval(
        instance, profile, budget_multiplier=1
    )
    print(len(winners_fast))
    print(winners_fast)
    winners_slow = method_of_equal_shares(
        instance,
        profile.as_multiprofile(),
        sat_class=Cost_Sat,
        voter_budget_increment=1,
        verbose=False,
        resoluteness=False,
    )
    print(len(winners_slow))
    print(f"{winners_slow} - {winners_slow == winners_fast}")
    # winners_slow = naive_mes(instance, profile, Cost_Sat, frac(instance.budget_limit, profile.num_ballots()))
    # print(len(winners_slow))
    # print(f"{winners_slow} - {winners_slow == winners_fast}")
    #
    # winners_slow = naive_mes(instance, profile, Cost_Sat, frac(instance.budget_limit, profile.num_ballots()), afford_func=is_affordable2)
    # print(len(winners_slow))
    # print(f"{winners_slow} - {winners_slow == winners_fast}")
    # winners_slow = method_of_equal_shares(
    #     instance,
    #     profile.as_multiprofile(),
    #     sat_class=Cost_Sat,
    #     budget_step=len(profile),
    #     binary_sat=False,
    # )
    # print(len(winners_slow))
    # print(winners_slow)

    # print(profile.approval_score(instance.get_project("24")))
    # print(profile.approval_score(instance.get_project("41")))
