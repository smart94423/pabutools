from unittest import TestCase

from pabutools.election.profile import ApprovalProfile
from pabutools.election.ballot import ApprovalBallot
from pabutools.tiebreaking import *


class TestTieBreaking(TestCase):
    def test_tie_breaking_rules(self):
        p = [
            Project("p0", 1),
            Project("p1", 3),
            Project("p2", 2),
            Project("p3", 1),
            Project("p4", 7),
            Project("p5", 5),
        ]
        instance = Instance(p)
        profile = ApprovalProfile(
            [
                ApprovalBallot([p[2], p[3]]),
                ApprovalBallot([p[2], p[4]]),
                ApprovalBallot(p),
                ApprovalBallot([p[2], p[3]]),
            ]
        )

        assert lexico_tie_breaking.untie(instance, profile, p) == p[0]
        assert lexico_tie_breaking.order(instance, profile, p) == p
        assert lexico_tie_breaking.untie(instance, profile, p[3:]) == p[3]
        assert lexico_tie_breaking.order(instance, profile, p[3:]) == p[3:]

        assert app_score_tie_breaking.untie(instance, profile, p) == p[2]
        assert app_score_tie_breaking.order(instance, profile, p)[:3] == [
            p[2],
            p[3],
            p[4],
        ]
        assert app_score_tie_breaking.untie(instance, profile, p[3:]) == p[3]
        assert app_score_tie_breaking.order(instance, profile, p[3:])[:2] == [
            p[3],
            p[4],
        ]

        assert min_cost_tie_breaking.untie(instance, profile, p) in (p[0], p[3])
        assert min_cost_tie_breaking.order(instance, profile, p) in (
            [p[0], p[3], p[2], p[1], p[5], p[4]],
            [p[3], p[0], p[2], p[1], p[5], p[4]],
        )
        assert min_cost_tie_breaking.untie(instance, profile, p[3:]) == p[3]
        assert min_cost_tie_breaking.order(instance, profile, p[3:]) == [
            p[3],
            p[5],
            p[4],
        ]

        assert max_cost_tie_breaking.untie(instance, profile, p) == p[4]
        assert max_cost_tie_breaking.order(instance, profile, p) in (
            [p[4], p[5], p[1], p[2], p[3], p[0]],
            [p[4], p[5], p[1], p[2], p[0], p[3]],
        )
        assert max_cost_tie_breaking.untie(instance, profile, p[3:]) == p[4]
        assert max_cost_tie_breaking.order(instance, profile, p[3:]) == [
            p[4],
            p[5],
            p[3],
        ]

        with self.assertRaises(TieBreakingException):
            refuse_tie_breaking.untie(instance, profile, p)
        with self.assertRaises(TieBreakingException):
            refuse_tie_breaking.order(instance, profile, p)
