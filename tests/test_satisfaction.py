from copy import deepcopy
from unittest import TestCase

import numpy as np

from pabutools.election import FrozenApprovalBallot
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
from tests.test_class_inheritence import check_members_equality


class TestSatisfaction(TestCase):
    def test_satisfaction_measure(self):
        sat1 = Cost_Sat(
            Instance(), ApprovalProfile(), FrozenApprovalBallot([Project("p1", 1)])
        )
        sat2 = Cost_Sat(
            Instance(), ApprovalProfile(), FrozenApprovalBallot([Project("p2", 1)])
        )

        # Test print outcome
        sat1.__str__()
        sat1.__repr__()

        # Test operations on sat measures
        assert sat1 == sat1
        assert sat1 <= sat1
        assert sat1 >= sat1
        assert sat1 != sat2
        assert sat1 <= sat2
        assert not sat2 <= sat1
        assert sat1 < sat2
        assert not sat2 < sat2
        assert sat1 != "qsd"
        assert not sat1 <= "qsd"
        assert not sat1 < "qsd"

    def test_satisfaction_profile(self):
        instance = get_random_instance(10, 1, 10)
        profile = get_random_approval_profile(instance, 30)

        # Test error when either a profile or a satisfaction measure is not given
        with self.assertRaises(TypeError):
            SatisfactionProfile(sat_class=CC_Sat)
        with self.assertRaises(TypeError):
            SatisfactionProfile(profile=profile)

        # Test that the sat profile is correctly initialised
        sat_profile = SatisfactionProfile(sat_class=CC_Sat, profile=profile)
        assert len(sat_profile) == len(profile)

        # Test operations on satisfaction profiles
        sat_profile2 = deepcopy(sat_profile)
        assert len(sat_profile) == len(sat_profile2)
        sat_profile3 = sat_profile + sat_profile2
        assert len(sat_profile3) == 2 * len(profile)
        sat_profile3 *= 4
        assert len(sat_profile3) == 8 * len(profile)

        # Test constructor from another sat profile
        new_sat_profile = SatisfactionProfile(sat_profile)
        check_members_equality(sat_profile, new_sat_profile)

        # Test empty constructor
        SatisfactionProfile()

    def test_satisfaction_multiprofile(self):
        instance = get_random_instance(10, 1, 10)
        profile = get_random_approval_profile(instance, 30)
        multiprofile = profile.as_multiprofile()

        # Test extend
        sat_multiprofile = multiprofile.as_sat_profile(Cost_Log_Sat)
        assert len(sat_multiprofile) == len(multiprofile)
        assert sat_multiprofile.total() == multiprofile.total()
        sat_multiprofile.extend_from_multiprofile(multiprofile, Cost_Log_Sat)
        assert len(sat_multiprofile) == len(multiprofile)
        assert sat_multiprofile.total() == multiprofile.total() * 2

        # Test error when either a profile or a satisfaction measure is not given
        with self.assertRaises(TypeError):
            SatisfactionMultiProfile(sat_class=CC_Sat)
        with self.assertRaises(TypeError):
            SatisfactionMultiProfile(profile=profile)
        with self.assertRaises(TypeError):
            SatisfactionMultiProfile(multiprofile=multiprofile)

        # Test that the sat profile is correctly initialised
        sat_multiprofile1 = SatisfactionMultiProfile(sat_class=CC_Sat, profile=profile)
        assert len(sat_multiprofile1) == len(multiprofile)
        sat_multiprofile2 = SatisfactionMultiProfile(
            sat_class=CC_Sat, multiprofile=multiprofile
        )
        assert len(sat_multiprofile2) == len(multiprofile)

        # Test constructor from another sat multiprofile
        new_sat_multiprofile = SatisfactionMultiProfile(sat_multiprofile1)
        check_members_equality(sat_multiprofile1, new_sat_multiprofile)

        # Test empty constructor
        SatisfactionMultiProfile()

        # Test equivalence with simple profile
        for sat_class in [
            Cost_Sat,
            Relative_Cost_Sat,
            Relative_Cost_Approx_Normaliser_Sat,
            Cardinality_Sat,
            Relative_Cardinality_Sat,
            Effort_Sat,
            Cost_Log_Sat,
            Cost_Sqrt_Sat,
            CC_Sat,
        ]:
            for _ in range(1):
                instance = get_random_instance(100, 0, 100)
                profile = get_random_approval_profile(instance, 100)
                sat_profile = SatisfactionProfile(
                    instance=instance, profile=profile, sat_class=sat_class
                )
                total_sat1 = sat_profile.total_satisfaction(list(instance)[:20])
                sat_multiprofile = SatisfactionMultiProfile(
                    instance=instance, profile=profile, sat_class=sat_class
                )
                total_sat2 = sat_multiprofile.total_satisfaction(list(instance)[:20])
                assert total_sat1 == total_sat2

    def test_cc_sat(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = deepcopy(b1)
        b3 = ApprovalBallot((projects[0], projects[1]))
        b4 = ApprovalBallot((projects[2], projects[3]))
        b5 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2, b3, b4, b5], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=CC_Sat)
        assert sat_profile[0].sat([projects[0]]) == 1
        assert sat_profile[0].sat(projects[:4]) == 1
        assert sat_profile[0].sat(projects) == 1
        assert sat_profile[2].sat(projects[2:]) == 0
        assert sat_profile[4].sat(projects) == 0

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
        b3 = CardinalBallot()
        profile = CardinalProfile((b1, b2, b3), instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=CC_Sat)
        assert sat_profile[0].sat([projects[0]]) == 0
        assert sat_profile[0].sat(projects[:4]) == 74
        assert sat_profile[0].sat(projects) == 74
        assert sat_profile[1].sat(projects[2:]) == 68
        assert sat_profile[2].sat(projects) == 0

        with self.assertRaises(ValueError):
            CC_Sat(Instance(), OrdinalProfile(), OrdinalBallot())

    def test_sqrt_sat(self):
        projects = [
            Project("p1", 9),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Sqrt_Sat)
        assert sat_profile[0].sat([projects[0]]) == 3
        assert sat_profile[0].sat(projects[1:3]) == 3
        assert sat_profile[1].sat(projects) == 0

        with self.assertRaises(ValueError):
            Cost_Sqrt_Sat(Instance(), OrdinalProfile(), OrdinalBallot())

    def test_log_sat(self):
        projects = [
            Project("p1", 0),
            Project("p2", 4),
            Project("p3", 4),
            Project("p4", 9),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Log_Sat)
        assert sat_profile[0].sat([projects[0]]) == 0
        assert sat_profile[0].sat(projects[1:4]) == np.log(1 + 4 + 4 + 9)
        assert sat_profile[1].sat(projects) == 0

        with self.assertRaises(ValueError):
            Cost_Log_Sat(Instance(), OrdinalProfile(), OrdinalBallot())

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
        b3 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2, b3], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cardinality_Sat)
        assert sat_profile[0].sat([projects[0]]) == 1
        assert sat_profile[0].sat(projects[:4]) == 4
        assert sat_profile[0].sat(projects) == 4
        assert sat_profile[1].sat(projects[2:]) == 0
        assert sat_profile[2].sat(projects) == 0

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
        b3 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2, b3], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Cost_Sat)
        assert sat_profile[0].sat([projects[0]]) == 9
        assert sat_profile[0].sat(projects[:4]) == 34
        assert sat_profile[0].sat(projects) == 34
        assert sat_profile[1].sat(projects[2:]) == 0
        assert sat_profile[2].sat(projects) == 0

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
        b4 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2, b3, b4], instance=instance)
        sat_profile = SatisfactionProfile(
            profile=profile, instance=instance, sat_class=Relative_Cardinality_Sat
        )
        assert sat_profile[0].sat([projects[0]]) == frac(1, 3)
        assert sat_profile[0].sat(projects[1:]) == 1
        assert sat_profile[1].sat(projects[2:]) == 0
        assert sat_profile[2].sat([]) == 0
        assert sat_profile[3].sat(projects) == 0

    def test_rel_cost_sat(self):
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
        b4 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2, b3, b4], instance=instance)
        sat_profile = SatisfactionProfile(
            profile=profile, instance=instance, sat_class=Relative_Cost_Sat
        )
        assert sat_profile[0].precomputed_values["max_budget_allocation_cost"] == 6
        assert sat_profile[0].sat([projects[0]]) == frac(4, 6)
        assert sat_profile[0].sat(projects[1:]) == 1
        assert sat_profile[1].sat(projects[1:]) == frac(2, 6)
        assert sat_profile[2].sat([]) == 0
        assert sat_profile[3].sat(projects) == 0

    def test_rel_card_unbounded_sat(self):
        projects = [
            Project("p1", 4),
            Project("p2", 2),
            Project("p3", 3),
            Project("p4", 1),
            Project("p5", 20),
        ]
        instance_1 = Instance(projects, budget_limit=60)
        instance_2 = Instance(projects, budget_limit=7)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1]))
        b3 = ApprovalBallot((projects[4],))
        b4 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2, b3, b4], instance=instance_1)
        sat_profile_1 = SatisfactionProfile(
            profile=profile,
            instance=instance_1,
            sat_class=Relative_Cost_Approx_Normaliser_Sat,
        )
        assert sat_profile_1[0].sat([projects[0]]) == frac(4, 10)
        assert sat_profile_1[0].sat(projects[1:]) == frac(6, 10)
        assert sat_profile_1[1].sat(projects[1:]) == frac(2, 6)
        assert sat_profile_1[2].sat([]) == 0
        assert sat_profile_1[3].sat(projects) == 0

        sat_profile_2 = SatisfactionProfile(
            profile=profile,
            instance=instance_2,
            sat_class=Relative_Cost_Approx_Normaliser_Sat,
        )
        assert sat_profile_2[0].sat([projects[0]]) == frac(4, 7)
        assert sat_profile_2[0].sat(projects[1:]) == frac(6, 7)
        assert sat_profile_2[1].sat(projects[1:]) == frac(2, 6)
        assert sat_profile_2[2].sat(projects[:3]) == 0
        assert sat_profile_2[3].sat(projects) == 0

    def test_effot_sat(self):
        projects = [
            Project("p1", 8),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
            Project("p5", 1),
        ]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1]))
        b3 = ApprovalBallot()
        profile = ApprovalProfile([b1, b2, b3], instance=instance)
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Effort_Sat)
        assert sat_profile[0].sat([projects[0]]) == 4
        assert sat_profile[0].sat(projects[:4]) == 4 + 2 + 5 + 16
        assert sat_profile[0].sat(projects) == 4 + 2 + 5 + 16
        assert sat_profile[1].sat(projects[2:]) == 0
        assert sat_profile[2].sat(projects) == 0

    def test_cardinal_sat(self):
        projects = [
            Project("p1", 8),
            Project("p2", 4),
            Project("p3", 5),
            Project("p4", 16),
            Project("p5", 16),
            Project("p6", 16),
        ]
        instance = Instance(projects, budget_limit=30)
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
        profile = CardinalProfile((b1, b2), instance=instance)
        sat_profile = SatisfactionProfile(
            profile=profile, sat_class=Additive_Cardinal_Sat
        )
        assert sat_profile[0].sat([projects[0]]) == 0
        assert sat_profile[0].sat(projects[:4]) == 4 + 74 + 12
        assert sat_profile[0].sat(projects) == 4 + 74 + 12 + 7 - 41
        assert sat_profile[1].sat(projects[2:]) == 4 + 68 + 7
        with self.assertRaises(ValueError):
            Additive_Cardinal_Sat(instance, profile, ApprovalBallot())

        sat_profile = SatisfactionProfile(
            profile=profile, sat_class=Additive_Cardinal_Relative_Sat
        )
        assert sat_profile[0].sat([projects[0]]) == 0
        assert sat_profile[0].sat(projects[:4]) == 1
        assert sat_profile[0].sat(projects) == frac(4 + 74 + 12 + 7 - 41, 90)
        with self.assertRaises(ValueError):
            Additive_Cardinal_Sat(instance, profile, ApprovalBallot())

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
        b4 = OrdinalBallot()
        profile = OrdinalProfile((b1, b2, b3, b4))
        sat_profile = SatisfactionProfile(profile=profile, sat_class=Additive_Borda_Sat)
        assert sat_profile[0].sat([projects[0]]) == 2
        assert sat_profile[0].sat(projects[:4]) == 2 + 1
        assert sat_profile[0].sat(projects) == 2 + 1
        assert sat_profile[1].sat(projects[2:]) == 2 + 1
        assert sat_profile[2].sat(projects[:2]) == 0
        assert sat_profile[3].sat(projects) == 0

        with self.assertRaises(ValueError):
            Additive_Borda_Sat(Instance(), ApprovalProfile(), ApprovalBallot())
