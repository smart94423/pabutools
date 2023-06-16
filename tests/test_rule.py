from unittest import TestCase
from pbvoting.fractions import frac
from pbvoting.instance.profile import ApprovalBallot, ApprovalProfile
from pbvoting.instance.satisfaction import Cost_Sat, Cardinality_Sat, Effort_Sat, Log_Sat, Cost_Sqrt_Sat, CC_Sat, \
    SatisfactionProfile
from pbvoting.instance.pbinstance import Project, PBInstance
from pbvoting.rules.phragmen import sequential_phragmen
from pbvoting.rules.exhaustion import completion_by_rule_combination, exhaustion_by_budget_increase
from pbvoting.rules.greedywelfare import greedy_welfare
from pbvoting.rules.maxwelfare import max_welfare
from pbvoting.rules.mes import method_of_equal_shares

ALL_SAT_RULES = [greedy_welfare, max_welfare, method_of_equal_shares]
ALL_NON_SAT_RULES = [sequential_phragmen]
ALL_SAT = [Cost_Sat, Cardinality_Sat, Effort_Sat, Log_Sat, Cost_Sqrt_Sat, CC_Sat]


class TestElection:

    def __init__(self, name="", projects=None, instance=None, profile=None):
        self.name = name
        self.projects = projects
        self.instance = instance
        self.profile = profile
        self.irr_results_sat = dict()
        for rule in ALL_SAT_RULES:
            self.irr_results_sat[rule] = dict()
            for sat in ALL_SAT:
                self.irr_results_sat[rule][sat] = None
        self.irr_results_non_sat = dict()
        for rule in ALL_NON_SAT_RULES:
            self.irr_results_non_sat[rule] = None


def test_elections():
    res = []

    # Approval example 1
    p = [Project("p0", 1), Project("p1", 3), Project("p2", 2), Project("p3", 1)]
    inst = PBInstance(p, budget_limit=3)
    prof = ApprovalProfile([
        ApprovalBallot((p[0], p[1], p[2], p[3])),
        ApprovalBallot((p[0], p[1], p[2], p[3])),
    ], instance=inst)
    test_election = TestElection("AppEx_1", p, inst, prof)
    test_election.irr_results_sat[greedy_welfare][Cost_Sat] = sorted([[p[0], p[2]], [p[0], p[3]], [p[1]], [p[2], p[3]]])
    test_election.irr_results_sat[greedy_welfare][Cardinality_Sat] = sorted([[p[0], p[3]]])
    test_election.irr_results_sat[max_welfare][Cost_Sat] = sorted([[p[0], p[2]], [p[1]], [p[2], p[3]]])
    test_election.irr_results_sat[max_welfare][Cardinality_Sat] = sorted([[p[0], p[3]], [p[0], p[2]], [p[2], p[3]]])
    res.append(test_election)

    # Approval example 2
    p = [Project("p0", 1), Project("p1", 0.9), Project("p2", 2), Project("p3", 1.09)]
    inst = PBInstance(p, budget_limit=4)
    prof = ApprovalProfile([
        ApprovalBallot({p[0]}),
        ApprovalBallot({p[1], p[2], p[3]}),
        ApprovalBallot({p[1], p[2], p[3]}),
        ApprovalBallot({p[2]})
    ], instance=inst)
    test_election = TestElection("AppEx_2", p, inst, prof)
    test_election.irr_results_sat[method_of_equal_shares][Cardinality_Sat] = sorted([[p[0], p[1], p[3]]])
    test_election.irr_results_sat[method_of_equal_shares][Cost_Sat] = sorted([[p[0], p[2]]])
    res.append(test_election)

    # Empty profile
    p = [Project("p0", 1), Project("p1", 3), Project("p2", 2), Project("p3", 1)]
    inst = PBInstance(p, budget_limit=3)
    prof = ApprovalProfile([ApprovalBallot()], instance=inst)
    test_election = TestElection("EmptyProfile", p, inst, prof)

    for sat_class in ALL_SAT:
        test_election.irr_results_sat[max_welfare][sat_class] = sorted(
            [sorted(list(b)) for b in inst.budget_allocations()])
        test_election.irr_results_sat[greedy_welfare][sat_class] = sorted(
            [sorted(list(b)) for b in inst.budget_allocations()
             if inst.is_exhaustive(b)])
        test_election.irr_results_sat[method_of_equal_shares][sat_class] = [[]]
    test_election.irr_results_non_sat[sequential_phragmen] = [[p[0]], [p[1]], [p[2]], [p[3]]]
    res.append(test_election)

    # Running example from Lackner & Skowron 2023
    p = [
        Project("a", 1),
        Project("b", 1),
        Project("c", 1),
        Project("d", 1),
        Project("e", 1),
        Project("f", 1),
        Project("g", 1),
    ]
    inst = PBInstance(p, budget_limit=4)
    prof = ApprovalProfile([
        ApprovalBallot({p[0], p[1]}),
        ApprovalBallot({p[0], p[1]}),
        ApprovalBallot({p[0], p[1]}),
        ApprovalBallot({p[0], p[2]}),
        ApprovalBallot({p[0], p[2]}),
        ApprovalBallot({p[0], p[2]}),
        ApprovalBallot({p[0], p[3]}),
        ApprovalBallot({p[0], p[3]}),
        ApprovalBallot({p[1], p[2], p[5]}),
        ApprovalBallot({p[4]}),
        ApprovalBallot({p[5]}),
        ApprovalBallot({p[6]})
    ], instance=inst)
    test_election = TestElection("RunningEx LackSkow23", p, inst, prof)
    test_election.irr_results_non_sat[sequential_phragmen] = sorted([p[:4]])
    for sat_class in [Cost_Sat, Cardinality_Sat, Cost_Sqrt_Sat, Log_Sat]:
        test_election.irr_results_sat[method_of_equal_shares][sat_class] = sorted([[p[0]]])
    res.append(test_election)

    return res


ALL_TEST_ELECTIONS = test_elections()


def run_sat_rule(rule):
    for test_election in ALL_TEST_ELECTIONS:
        for sat_class in test_election.irr_results_sat[rule]:
            if test_election.irr_results_sat[rule][sat_class] is not None:
                print("\n===================== {} - {} =====================".format(rule.__name__,
                                                                                     sat_class.__name__))
                print("Test `{}`\nInst: {}\n Profile: {}".format(test_election.name, test_election.instance,
                                                                 test_election.profile))
                resolute_out = rule(test_election.instance, test_election.profile, sat_class=sat_class,
                                    resoluteness=True)
                irresolute_out = sorted(rule(test_election.instance, test_election.profile, sat_class=sat_class,
                                             resoluteness=False))
                print("Irres outcome:  {}".format(irresolute_out))
                print("Irres expected: {}".format(test_election.irr_results_sat[rule][sat_class]))
                assert resolute_out in test_election.irr_results_sat[rule][sat_class]
                assert resolute_out == rule(test_election.instance, test_election.profile, resoluteness=True,
                                            sat_profile=SatisfactionProfile(profile=test_election.profile,
                                                                            sat_class=sat_class))
                assert irresolute_out == test_election.irr_results_sat[rule][sat_class]


def run_non_sat_rule(rule):
    for test_election in ALL_TEST_ELECTIONS:
        if test_election.irr_results_non_sat[rule] is not None:
            print("\n===================== {} =====================".format(rule.__name__))
            print("Test `{}`\nInst: {}\n Profile: {}".format(test_election.name, test_election.instance,
                                                             test_election.profile))
            resolute_out = sorted(rule(test_election.instance, test_election.profile, resoluteness=True))
            irresolute_out = sorted(rule(test_election.instance, test_election.profile, resoluteness=False))
            print("Irres outcome:  {}".format(irresolute_out))
            print("Irres expected: {}".format(test_election.irr_results_non_sat[rule]))
            assert resolute_out in test_election.irr_results_non_sat[rule]
            assert irresolute_out == test_election.irr_results_non_sat[rule]


class TestRule(TestCase):

    def test_greedy_welfare(self):
        run_sat_rule(greedy_welfare)

    def test_max_welfare(self):
        run_sat_rule(max_welfare)

    def test_phragmen(self):
        run_non_sat_rule(sequential_phragmen)

    def test_mes_approval(self):
        run_sat_rule(method_of_equal_shares)

    def test_iterated_exhaustion(self):
        projects = [
            Project("a", 1),
            Project("b", 1),
            Project("c", 1),
            Project("d", 1),
            Project("e", 1),
            Project("f", 1),
            Project("g", 1),
        ]
        instance = PBInstance(projects, budget_limit=4)
        profile = ApprovalProfile(
            [
                ApprovalBallot({projects[0], projects[1]}),
                ApprovalBallot({projects[0], projects[1]}),
                ApprovalBallot({projects[0], projects[1]}),
                ApprovalBallot({projects[0], projects[2]}),
                ApprovalBallot({projects[0], projects[2]}),
                ApprovalBallot({projects[0], projects[2]}),
                ApprovalBallot({projects[0], projects[3]}),
                ApprovalBallot({projects[0], projects[3]}),
                ApprovalBallot({projects[1], projects[2], projects[5]}),
                ApprovalBallot({projects[4]}),
                ApprovalBallot({projects[5]}),
                ApprovalBallot({projects[6]})
            ]
        )
        budget_allocation_mes = method_of_equal_shares(instance, profile, Cost_Sat)
        assert budget_allocation_mes == [projects[0]]

        budget_allocation_mes_iterated = exhaustion_by_budget_increase(instance,
                                                                       profile,
                                                                       method_of_equal_shares,
                                                                       {"sat_class": Cost_Sat},
                                                                       budget_step=frac(1, 24))
        assert budget_allocation_mes_iterated == [projects[0], projects[1], projects[2], projects[3]]

        budget_allocation_mes_iterated_big_steps = exhaustion_by_budget_increase(instance,
                                                                                 profile,
                                                                                 method_of_equal_shares,
                                                                                 {"sat_class": Cost_Sat},
                                                                                 budget_step=5)
        assert budget_allocation_mes_iterated_big_steps == [projects[0]]

    def test_completion(self):
        projects = [
            Project("a", 1),
            Project("b", 2),
            Project("c", 2),
            Project("d", 1),
            Project("e", 1),
            Project("f", 1),
            Project("g", 1),
        ]
        instance = PBInstance(projects, budget_limit=5)
        profile = ApprovalProfile(
            [
                ApprovalBallot({projects[0], projects[1]}),
                ApprovalBallot({projects[0], projects[1]}),
                ApprovalBallot({projects[0]}),
                ApprovalBallot({projects[0], projects[2]}),
                ApprovalBallot({projects[0], projects[2]}),
                ApprovalBallot({projects[0], projects[2]}),
                ApprovalBallot({projects[0], projects[3]}),
                ApprovalBallot({projects[0], projects[3]}),
                ApprovalBallot({projects[5]}),
                ApprovalBallot({projects[4]})
            ]
        )
        budget_allocation_mes = method_of_equal_shares(instance, profile, Cost_Sat)
        assert budget_allocation_mes == [projects[0]]

        budget_allocation_mes_iterated = completion_by_rule_combination(instance,
                                                                        profile,
                                                                        [method_of_equal_shares,
                                                                         greedy_welfare],
                                                                        [{"sat_class": Cost_Sat},
                                                                         {"sat_class": Cost_Sat}])
        assert budget_allocation_mes_iterated == [projects[0], projects[2], projects[1]]

        self.assertRaises(Exception, lambda: completion_by_rule_combination(instance,
                                                                            profile,
                                                                            [method_of_equal_shares,
                                                                             greedy_welfare],
                                                                            [{"sat_class": Cost_Sat}]))
        self.assertRaises(ValueError, lambda: completion_by_rule_combination(instance,
                                                                             profile,
                                                                             [method_of_equal_shares,
                                                                              greedy_welfare]))
