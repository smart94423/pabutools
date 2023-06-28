
from unittest import TestCase

import numpy as np

from pbvoting.election.profile import ApprovalProfile, CardinalProfile, OrdinalProfile, get_random_approval_profile
from pbvoting.election.instance import Instance, Project, get_random_instance
from pbvoting.election.ballot import ApprovalBallot, CardinalBallot, OrdinalBallot
from pbvoting.election.satisfaction import *


class TestSatisfaction(TestCase):

    def test_total_sat(self):
        instance = get_random_instance(100, 0, 100)
        profile = get_random_approval_profile(instance, 100)
        sat_profile = SatisfactionProfile(instance=instance, profile=profile, sat_class=Cost_Sat)
        sat_multiprofile = SatisfactionMultiProfile(instance=instance, profile=profile, sat_class=Cost_Sat)
        assert sat_profile.total_satisfaction(list(instance)[:20]) == sat_multiprofile.total_satisfaction(list(instance)[:20])

        p = [Project("p0", 1), Project("p1", 0.9), Project("p2", 2), Project("p3", 1.09), Project("p4", 1.09),
             Project("p5", 1.09)]
        inst = Instance(p, budget_limit=4)
        prof = ApprovalProfile([
            ApprovalBallot({p[0]}),
            ApprovalBallot({p[1], p[2], p[3]}),
            ApprovalBallot({p[1], p[2], p[3]}),
            ApprovalBallot({p[2]})
        ], instance=inst)
        sat_profile = SatisfactionProfile(instance=inst, profile=prof, sat_class=Cost_Sat)
        sat_multiprofile = SatisfactionMultiProfile(instance=inst, profile=prof, sat_class=Cost_Sat)
        for proj in p:
            assert sat_profile.total_satisfaction([proj]) == sat_multiprofile.total_satisfaction([proj])
