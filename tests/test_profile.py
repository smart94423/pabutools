from unittest import TestCase

from pbvoting.election import (
    Instance,
    Project,
    ApprovalProfile,
    CardinalProfile,
    CumulativeProfile,
    OrdinalProfile,
    get_random_approval_profile,
    get_all_approval_profiles,
    ApprovalBallot,
    CardinalBallot,
    CumulativeBallot,
    OrdinalBallot,
    FrozenApprovalBallot,
    ApprovalMultiProfile,
    FrozenCardinalBallot,
    CardinalMultiProfile,
)


class TestProfile(TestCase):
    # def test_profile(self):
    #     profile = Profile()
    #     b1 = Ballot()
    #     b2 = Ballot()
    #     b3 = Ballot()
    #
    #     profile = profile.__add__(Profile([b1, b2]))
    #     assert len(profile) == 2
    #     profile *= 3
    #     assert len(profile) == 6
    #     profile.append(b3)
    #     assert len(profile) == 7
    #     profile.insert(1, b1)
    #     assert profile[1] == b1
    #     assert profile[2] == b2
    #     assert len(profile) == 8
    #     profile.__setitem__(0, b3)
    #     assert profile[0] == b3
    #     profile.extend(Profile([b1, b1]))
    #     assert len(profile) == 10
    #     assert profile[-1] == b1
    #     assert profile[-2] == b1
    #     profile.extend((b2, b2,))
    #     assert len(profile) == 12
    #     assert profile[-1] == b2
    #     assert profile[-2] == b2

    def test_approval_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
        b1 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b2 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        b3 = ApprovalBallot((projects[0], projects[1], projects[2], projects[3]))
        profile = ApprovalProfile((b1, b2, b3), instance=instance)
        assert profile.is_party_list() is True
        b4 = ApprovalBallot((projects[4], projects[5]))
        b5 = ApprovalBallot((projects[4], projects[5]))
        profile = profile.__add__([b4, b5])
        assert len(profile) == 5
        assert profile.is_party_list() is True
        b6 = ApprovalBallot([projects[0], projects[4]])
        profile.append(b6)
        assert profile.is_party_list() is False
        assert len(profile.approved_projects()) == 6
        assert profile.is_trivial() is True
        instance.budget_limit = 3
        assert profile.is_trivial() is False

        card_ballot = CardinalBallot({projects[1]: 5, projects[2]: 2})
        with self.assertRaises(TypeError):
            profile.append(card_ballot)
        with self.assertRaises(TypeError):
            ApprovalProfile((card_ballot))

        profile.ballot_validation = False
        profile.append(card_ballot)

        profile.legal_min_length = 1
        profile.legal_max_length = 5
        profile.legal_min_cost = 10
        profile.legal_max_cost = 100
        profile2 = ApprovalProfile([b1, b2, b3])
        profile3 = profile.__add__(profile2)
        assert len(profile3) == 10
        assert profile3[0] == b1
        assert profile3[1] == b2
        assert profile3[2] == b3
        assert profile3[3] == b4
        assert profile3[4] == b5
        assert profile3[5] == b6
        assert profile3[6] == card_ballot
        assert profile3[7] == b1
        assert profile3[8] == b2
        assert profile3[9] == b3
        assert profile.legal_min_length == 1
        assert profile.legal_max_length == 5
        assert profile.legal_min_cost == 10
        assert profile.legal_max_cost == 100

        profile2.legal_min_length = 1
        profile2.legal_max_length = 5
        profile2.legal_min_cost = 10
        profile2.legal_max_cost = 100
        profile2 *= 3
        assert len(profile2) == 9
        assert profile2[0] == profile2[3] == profile2[6]
        assert profile2[1] == profile2[4] == profile2[7]
        assert profile2[2] == profile2[5] == profile2[8]
        assert profile2.legal_min_length == 1
        assert profile2.legal_max_length == 5
        assert profile2.legal_min_cost == 10
        assert profile2.legal_max_cost == 100

        random_profile = get_random_approval_profile(instance, 10)
        assert len(random_profile) == 10

        new_inst = Instance(
            [Project("p1", 1), Project("p2", 1), Project("p3", 1)], budget_limit=3
        )
        assert len(set(get_all_approval_profiles(new_inst, 1))) == 8
        assert len(set(get_all_approval_profiles(new_inst, 2))) == 8 * 8
        assert len(set(get_all_approval_profiles(new_inst, 3))) == 8 * 8 * 8

    def test_app_multiprofile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b1 = FrozenApprovalBallot(projects[:4], name="name", meta={"metakey": 0})
        b2 = FrozenApprovalBallot(projects[1:6], name="name", meta={"metakey": 0})
        b3 = FrozenApprovalBallot({projects[0]}, name="name", meta={"metakey": 0})
        b4 = FrozenApprovalBallot(
            (projects[1], projects[4]), name="name", meta={"metakey": 0}
        )
        multiprofile = ApprovalMultiProfile((b1, b2, b3, b4))
        assert len(multiprofile) == 4
        assert multiprofile.total() == 4
        multiprofile.append(b1)
        assert len(multiprofile) == 4
        assert multiprofile.total() == 5

        profile = ApprovalProfile(
            [ApprovalBallot(projects[:2])] * 4 + [ApprovalBallot(projects[:5])] * 10
        )
        assert len(profile) == 14
        multiprofile = ApprovalMultiProfile(profile=profile)
        assert len(multiprofile) == 2
        assert multiprofile.total() == 14

    def test_cardinal_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
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
        b3 = CardinalBallot(
            {
                projects[1]: 57,
                projects[2]: 5,
                projects[3]: 5857,
                projects[4]: 7786,
                projects[5]: -481,
            }
        )
        b4 = CardinalBallot(
            {
                projects[1]: 2,
                projects[2]: 8,
                projects[3]: 16872,
                projects[4]: 77,
                projects[5]: -457851,
            }
        )
        profile = CardinalProfile((b1, b2), instance=instance)
        assert len(profile) == 2
        assert profile[0] == b1
        assert profile[1] == b2

        profile.legal_min_length = 1
        profile.legal_max_length = 5
        profile.legal_min_score = 3
        profile.legal_max_score = 100
        profile = profile.__add__(CardinalProfile([b3, b4]))
        assert profile[2] == b3
        assert profile[3] == b4
        assert profile.legal_min_length == 1
        assert profile.legal_max_length == 5
        assert profile.legal_min_score == 3
        assert profile.legal_max_score == 100
        profile *= 10
        assert len(profile) == 40
        assert profile[0] == profile[4] == profile[8] == profile[12]
        assert profile[1] == profile[5] == profile[9] == profile[13]
        assert profile[2] == profile[6] == profile[10] == profile[14]
        assert profile[3] == profile[7] == profile[11] == profile[15]
        assert profile.legal_min_length == 1
        assert profile.legal_max_length == 5
        assert profile.legal_min_score == 3
        assert profile.legal_max_score == 100

    def test_cumulative_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
        b1 = CumulativeBallot(
            {
                projects[1]: 4,
                projects[2]: 74,
                projects[3]: 12,
                projects[4]: 7,
                projects[5]: -41,
            }
        )
        b2 = CumulativeBallot(
            {
                projects[1]: 41,
                projects[2]: 4,
                projects[3]: 68,
                projects[4]: 7,
                projects[5]: 0,
            }
        )
        b3 = CumulativeBallot(
            {
                projects[1]: 57,
                projects[2]: 5,
                projects[3]: 5857,
                projects[4]: 7786,
                projects[5]: -481,
            }
        )
        b4 = CumulativeBallot(
            {
                projects[1]: 2,
                projects[2]: 8,
                projects[3]: 16872,
                projects[4]: 77,
                projects[5]: -457851,
            }
        )
        profile = CumulativeProfile((b1, b2, b3), instance=instance)
        assert len(profile) == 3
        assert profile[0] == b1
        assert profile[1] == b2
        assert profile[2] == b3

        profile.legal_min_length = 6
        profile.legal_max_length = 7
        profile.legal_min_score = 6
        profile.legal_max_score = 10
        profile.legal_min_total_score = 1
        profile.legal_max_total_score = 1000
        profile = profile.__add__(CumulativeProfile([b4]))
        assert profile[3] == b4
        assert profile.legal_min_length == 6
        assert profile.legal_max_length == 7
        assert profile.legal_min_score == 6
        assert profile.legal_max_score == 10
        assert profile.legal_min_total_score == 1
        assert profile.legal_max_total_score == 1000
        profile *= 4
        assert len(profile) == 16
        assert profile[0] == profile[4] == profile[8] == profile[12]
        assert profile[1] == profile[5] == profile[9] == profile[13]
        assert profile[2] == profile[6] == profile[10] == profile[14]
        assert profile[3] == profile[7] == profile[11] == profile[15]
        assert profile[3] == b4
        assert profile.legal_min_length == 6
        assert profile.legal_max_length == 7
        assert profile.legal_min_score == 6
        assert profile.legal_max_score == 10
        assert profile.legal_min_total_score == 1
        assert profile.legal_max_total_score == 1000

    def test_ordinal_profile(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        instance = Instance(projects, budget_limit=1)
        b1 = OrdinalBallot([projects[0], projects[1], projects[2]])
        b2 = OrdinalBallot([projects[4], projects[5], projects[3]])
        b3 = OrdinalBallot([projects[2], projects[3], projects[7]])
        profile = OrdinalProfile((b1, b2, b3), instance=instance)
        assert len(profile) == 3
        profile = profile.__add__(OrdinalProfile([b1, b2]))
        assert profile.instance == instance
        assert len(profile) == 5
        profile *= 5
        assert profile.instance == instance
        assert len(profile) == 25
