import profile
from unittest import TestCase
from pbvoting.fractions import frac
from pbvoting.instance.profile import ApprovalBallot, ApprovalProfile
from pbvoting.instance.satisfaction import Cost_Sat, Cardinality_Sat
from pbvoting.instance.pbinstance import Project, PBInstance
from pbvoting.rules.exhaustion import completion_by_rule_combination, exhaustion_by_budget_increase
from pbvoting.rules.greedywelfare import greedy_welfare_approval
from pbvoting.rules.mes import method_of_equal_shares


class TestRule(TestCase):
    def test_greedy_welfare_approval(self):
        projects = [Project("p1", 1), Project("p2", 3), Project("p3", 2), Project("p4", 1)]
        instance = PBInstance(projects, budget_limit=3)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        profile = ApprovalProfile([b1, b2], instance=instance)
        assert greedy_welfare_approval(instance, profile, sat_class=Cost_Sat) == ["p1", "p3"]
        assert greedy_welfare_approval(instance, profile, sat_class=Cardinality_Sat) == ["p1", "p4"]
        irresolute_out = [["p1", "p3"], ["p1", "p4"], ["p2"], ["p3", "p4"]]
        assert greedy_welfare_approval(instance, profile, sat_class=Cost_Sat, resoluteness=False) == irresolute_out

    def test_mes_approval(self):
        projects = [Project("p0", 1), Project("p1", 0.9), Project("p2", 2), Project("p3", 1.09)]
        instance = PBInstance(projects, budget_limit=4)
        b1 = ApprovalBallot({projects[0]})
        b2 = ApprovalBallot({projects[1], projects[2], projects[3]})
        b3 = ApprovalBallot({projects[1], projects[2], projects[3]})
        b4 = ApprovalBallot({projects[2]})
        profile = ApprovalProfile([b1, b2, b3, b4], instance=instance)
        assert method_of_equal_shares(instance, profile, sat_class=Cost_Sat) == ["p0", "p2"]
        assert method_of_equal_shares(instance, profile, sat_class=Cardinality_Sat) == ["p0", "p1", "p3"]


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
                                                                       budget_step=frac(1,24))
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
                                                                        [method_of_equal_shares, greedy_welfare_approval],
                                                                        [{"sat_class": Cost_Sat}, {"sat_class": Cost_Sat}])
        assert budget_allocation_mes_iterated == [projects[0], projects[2], projects[1]]

        self.assertRaises(Exception, lambda: completion_by_rule_combination(instance,
                                                                            profile,
                                                                            [method_of_equal_shares, greedy_welfare_approval],
                                                                            [{"sat_class": Cost_Sat}]))
        self.assertRaises(ValueError, lambda: completion_by_rule_combination(instance,
                                                                             profile,
                                                                             [method_of_equal_shares, greedy_welfare_approval]))