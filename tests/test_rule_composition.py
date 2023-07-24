from unittest import TestCase

from pabutools.election import (
    Project,
    Instance,
    ApprovalProfile,
    ApprovalBallot,
    Cardinality_Sat,
    Cost_Sat,
)
from pabutools.rules import method_of_equal_shares, greedy_utilitarian_welfare
from pabutools.rules.composition import popularity_comparison


class TestRuleComposition(TestCase):
    def test_popularity_comparison(self):
        p = [Project("p0", 1), Project("p1", 3), Project("p2", 2), Project("p3", 1)]
        inst = Instance(p, budget_limit=3)
        prof = ApprovalProfile(
            [
                ApprovalBallot((p[0], p[1], p[2], p[3])),
                ApprovalBallot((p[0], p[1], p[2], p[3])),
            ],
            instance=inst,
        )
        results = popularity_comparison(
            inst,
            prof,
            Cardinality_Sat,
            [method_of_equal_shares, greedy_utilitarian_welfare],
            [{"sat_class": Cost_Sat}, {"sat_class": Cost_Sat}],
        )
        assert len(results) == 1
        assert results[0] == method_of_equal_shares(inst, prof, sat_class=Cost_Sat)
        assert results[0] == greedy_utilitarian_welfare(inst, prof, sat_class=Cost_Sat)

        p = [
            Project("p0", 1),
            Project("p1", 0.9),
            Project("p2", 2),
            Project("p3", 1.09),
            Project("p4", 1.09),
            Project("p5", 1.09),
        ]
        inst = Instance(p, budget_limit=4)
        prof = ApprovalProfile(
            [
                ApprovalBallot({p[0]}),
                ApprovalBallot({p[1], p[2], p[3]}),
                ApprovalBallot({p[1], p[2], p[3]}),
                ApprovalBallot({p[2]}),
            ],
            instance=inst,
        )
        results = popularity_comparison(
            inst,
            prof,
            Cardinality_Sat,
            [method_of_equal_shares, greedy_utilitarian_welfare],
            [{"sat_class": Cost_Sat}, {"sat_class": Cost_Sat}],
            initial_budget_allocation=[],
        )
        assert len(results) == 1
        assert results[0] == greedy_utilitarian_welfare(inst, prof, sat_class=Cost_Sat)

        with self.assertRaises(ValueError):
            popularity_comparison(
                inst,
                prof,
                Cardinality_Sat,
                [method_of_equal_shares, greedy_utilitarian_welfare],
                [{"sat_class": Cost_Sat}],
            )
