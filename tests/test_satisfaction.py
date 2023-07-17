from copy import deepcopy
from unittest import TestCase

import numpy as np

from pabutools.election.profile import (
    ApprovalProfile,
    CardinalProfile,
    OrdinalProfile,
    get_random_approval_profile,
)
from pabutools.election.instance import Instance, Project, get_random_instance
from pabutools.election.ballot import ApprovalBallot, CardinalBallot, OrdinalBallot
from pabutools.election.satisfaction import *
from pabutools.election.satisfaction.additivesatisfaction import (
    Relative_Cardinality_Sat,
    Relative_Cost_Sat,
    Relative_Cost_Approx_Normaliser_Sat,
)
from pabutools.fractions import frac


class TestSatisfaction(TestCase):
    def test_satisfaction_profile(self):
        instance = get_random_instance(10, 1, 10)
        profile = get_random_approval_profile(instance, 30)
        try:
            sat_profile = SatisfactionProfile(sat_class=CC_Sat)
        except TypeError:
            pass
        try:
            sat_profile = SatisfactionProfile(profile=profile)
        except TypeError:
            pass
        sat_profile = SatisfactionProfile(sat_class=CC_Sat, profile=profile)
        assert len(sat_profile) == len(profile)
        sat_profile2 = SatisfactionProfile(sat_class=CC_Sat, profile=profile)
        assert len(sat_profile2) == len(sat_profile2)
        sat_profile3 = sat_profile + sat_profile2
        assert len(sat_profile3) == 2 * len(profile)
        sat_profile3 *= 4
        assert len(sat_profile3) == 8 * len(profile)

    def test_cc_sat(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = deepcopy(b1)
        b3 = ApprovalBallot((projects[0], projects[1]))
        b4 = ApprovalBallot((projects[2], projects[3]))
        profile = ApprovalProfile([b1, b2, b3, b4], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=CC_Sat)
        assert sat_profile[0].sat([projects[0]]) == 1
        assert sat_profile[0].sat(projects[:4]) == 1
        assert sat_profile[0].sat(projects) == 1
        assert sat_profile[2].sat(projects[2:]) == 0

    def test_sqrt_sat(self):
        projects = [
            Project("p1", 9),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        profile = ApprovalProfile([b1], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Sqrt_Sat)
        assert sat_profile[0].sat([projects[0]]) == 3
        assert sat_profile[0].sat(projects[1:3]) == 3

    def test_log_sat(self):
        projects = [
            Project("p1", 0),
            Project("p2", 4),
            Project("p3", 4),
            Project("p4", 9),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        profile = ApprovalProfile([b1], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Log_Sat)
        assert sat_profile[0].sat([projects[0]]) == 0
        assert sat_profile[0].sat(projects[1:4]) == np.log(1 + 4 + 4 + 9)

    def test_card_sat(self):
        projects = [
            Project("p1", 9),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1]))
        profile = ApprovalProfile([b1, b2], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cardinality_Sat)
        assert sat_profile[0].sat([projects[0]]) == 1
        assert sat_profile[0].sat(projects[:4]) == 4
        assert sat_profile[0].sat(projects) == 4
        assert sat_profile[1].sat(projects[2:]) == 0

    def test_cost_sat(self):
        projects = [
            Project("p1", 9),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1]))
        profile = ApprovalProfile([b1, b2], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Sat)
        assert sat_profile[0].sat([projects[0]]) == 9
        assert sat_profile[0].sat(projects[:4]) == 34
        assert sat_profile[0].sat(projects) == 34
        assert sat_profile[1].sat(projects[2:]) == 0

    def test_rel_card_sat(self):
        projects = [
            Project("p1", 4),
            Project("p2", 2),
            Project("p3", 3),
            Project("p4", 1),
            Project("p5", 20),
        ]
        instance = Instance(projects, budget_limit=6)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1]))
        b3 = ApprovalBallot((projects[4],))
        profile = ApprovalProfile([b1, b2, b3], instance=instance)
        sat_profile = SatisfactionProfile(
            profile=profile, instance=instance, sat_class=Relative_Cardinality_Sat
        )
        assert sat_profile[0].sat([projects[0]]) == frac(1, 3)
        assert sat_profile[0].sat(projects[1:]) == 1
        assert sat_profile[1].sat(projects[2:]) == 0
        assert sat_profile[2].sat([]) == 0

    # def test_rel_card_sat(self):
    #     projects = [Project("p1", 4), Project("p2", 2), Project("p3", 3), Project("p4", 1), Project("p5", 20)]
    #     instance = Instance(projects, budget_limit=6)
    #     b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
    #     b2 = ApprovalBallot((projects[0], projects[1]))
    #     b3 = ApprovalBallot((projects[4],))
    #     profile = ApprovalProfile([b1, b2, b3], instance=instance)
    #     sat_profile = SatisfactionProfile(profile=profile, instance=instance, sat_class=Relative_Cost_Unbounded_Sat)
    #     assert sat_profile[0].sat([projects[0]]) == frac(4, 6)
    #     assert sat_profile[0].sat(projects[1:]) == 1
    #     assert sat_profile[1].sat(projects[1:]) == frac(2, 6)
    #     assert sat_profile[2].sat([]) == 0

    def test_rel_card_unbounded_sat(self):
        projects = [
            Project("p1", 4),
            Project("p2", 2),
            Project("p3", 3),
            Project("p4", 1),
            Project("p5", 20),
        ]
        instance = Instance(projects, budget_limit=6)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1]))
        b3 = ApprovalBallot((projects[4],))
        profile = ApprovalProfile([b1, b2, b3], instance=instance)
        sat_profile = SatisfactionProfile(
            profile=profile,
            instance=instance,
            sat_class=Relative_Cost_Approx_Normaliser_Sat,
        )
        assert sat_profile[0].sat([projects[0]]) == frac(4, 10)
        assert sat_profile[0].sat(projects[1:]) == frac(6, 10)
        assert sat_profile[1].sat(projects[1:]) == frac(2, 6)
        assert sat_profile[2].sat([]) == 0

    def test_effot_sat(self):
        projects = [
            Project("p1", 8),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1]))
        profile = ApprovalProfile([b1, b2], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Effort_Sat)
        assert sat_profile[0].sat([projects[0]]) == 4
        assert sat_profile[0].sat(projects[:4]) == 4 + 2 + 5 + 16
        assert sat_profile[0].sat(projects) == 4 + 2 + 5 + 16
        assert sat_profile[1].sat(projects[2:]) == 0

    def test_cardinal_sat(self):
        projects = [
            Project("p1", 8),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
            Project("p5", 16),
            Project("p6", 16),
        ]
        b1 = CardinalBallot(
            {
                projects[1]: 4,
                projects[2]: 74,
                projects[3]: 12,
                projects[4]: 7,
                projects[5]: -41,
            }
        )
        b2 = CardinalBallot(
            {
                projects[1]: 41,
                projects[2]: 4,
                projects[3]: 68,
                projects[4]: 7,
                projects[5]: 0,
            }
        )
        profile = CardinalProfile((b1, b2))
        sat_profile = SatisfactionProfile(
            profile=profile, sat_class=Additive_Cardinal_Sat
        )
        assert sat_profile[0].sat([projects[0]]) == 0
        assert sat_profile[0].sat(projects[:4]) == 4 + 74 + 12
        assert sat_profile[0].sat(projects) == 4 + 74 + 12 + 7 - 41
        assert sat_profile[1].sat(projects[2:]) == 4 + 68 + 7

    def test_borda_sat(self):
        projects = [
            Project("p1", 8),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
            Project("p5", 16),
            Project("p6", 16),
            Project("p7", 1),
            Project("p8", 5),
        ]
        b1 = OrdinalBallot([projects[0], projects[1], projects[2]])
        b2 = OrdinalBallot([projects[4], projects[5], projects[3]])
        b3 = OrdinalBallot([projects[2], projects[3], projects[7]])
        profile = OrdinalProfile((b1, b2, b3))
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Additive_Borda_Sat)
        assert sat_profile[0].sat([projects[0]]) == 2
        assert sat_profile[0].sat(projects[:4]) == 2 + 1
        assert sat_profile[0].sat(projects) == 2 + 1
        assert sat_profile[1].sat(projects[2:]) == 2 + 1
        assert sat_profile[2].sat(projects[:2]) == 0
