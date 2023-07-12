from unittest import TestCase


from pbvoting.election.profile import get_random_approval_profile
from pbvoting.election.instance import get_random_instance
from pbvoting.election.satisfaction import *


class TestSatisfaction(TestCase):
    def test_total_sat(self):
        for _ in range(10):
            instance = get_random_instance(100, 0, 100)
            profile = get_random_approval_profile(instance, 100)
            sat_profile = SatisfactionProfile(
                instance=instance, profile=profile, sat_class=Cost_Sat
            )
            total_sat1 = sat_profile.total_satisfaction(list(instance)[:20])
            sat_multiprofile = SatisfactionMultiProfile(
                instance=instance, profile=profile, sat_class=Cost_Sat
            )
            total_sat2 = sat_multiprofile.total_satisfaction(list(instance)[:20])
            assert total_sat1 == total_sat2
