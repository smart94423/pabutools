from unittest import TestCase

from pbvoting.election import SatisfactionMultiProfile, Cost_Sat
from pbvoting.election.profile import *


class TestMultiProfile(TestCase):

    def test_frozenballot(self):
        pass

    def test_multiprofile(self):
        pass

    def test_frozen_app_ballot(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b = FrozenApprovalBallot(projects[:4], name="name", meta={"metakey": 0})
        assert len(b) == 4
        assert projects[0] in b
        assert projects[1] in b
        assert projects[2] in b
        assert projects[3] in b
        assert b.name == "name"
        assert b.meta["metakey"] == 0

    def test_app_multiprofile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b1 = FrozenApprovalBallot(projects[:4], name="name", meta={"metakey": 0})
        b2 = FrozenApprovalBallot(projects[1:6], name="name", meta={"metakey": 0})
        b3 = FrozenApprovalBallot({projects[0]}, name="name", meta={"metakey": 0})
        b4 = FrozenApprovalBallot((projects[1], projects[4]), name="name", meta={"metakey": 0})
        multiprofile = ApprovalMultiProfile((b1, b2, b3, b4))
        assert len(multiprofile) == 4
        assert multiprofile.total() == 4
        multiprofile.append(b1)
        assert len(multiprofile) == 4
        assert multiprofile.total() == 5

        profile = ApprovalProfile([ApprovalBallot(projects[:2])] * 4 + [ApprovalBallot(projects[:5])] * 10)
        assert len(profile) == 14
        multiprofile = ApprovalMultiProfile(profile=profile)
        assert len(multiprofile) == 2
        assert multiprofile.total() == 14

    def test_frozen_card_ballot(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b = FrozenCardinalBallot({projects[0]: 1, projects[1]: 2, projects[2]: 4}, name="name", meta={"metakey": 0})
        assert b[projects[0]] == 1
        assert b[projects[1]] == 2
        assert b[projects[2]] == 4
        with self.assertRaises(ValueError):
            b[projects[3]] = 5

    def test_sat_multiprofile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        multiprofile = ApprovalMultiProfile([FrozenApprovalBallot(projects[:2])] * 4)
        profile = ApprovalProfile([ApprovalBallot(projects[:5])] * 10)
        multiprofile.extend(profile)

        sat_multi = SatisfactionMultiProfile(multiprofile=multiprofile, sat_class=Cost_Sat)
        sat_multi.extend_from_profile(profile, Cost_Sat)
