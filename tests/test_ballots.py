from unittest import TestCase

from pbvoting.election import Project, ApprovalBallot, CardinalBallot, CumulativeBallot, OrdinalBallot, \
    FrozenApprovalBallot, FrozenCardinalBallot, FrozenCumulativeBallot, FrozenOrdinalBallot
from tests.test_class_inheritence import check_members_equality


class TestBallot(TestCase):

    def test_init_with_ballots(self):
        p = [Project(str(i), i) for i in range(20)]

        b1 = ApprovalBallot(p, name="AppBallot", meta={"metakey": "metavalue"})
        b2 = ApprovalBallot(b1)
        check_members_equality(b1, b2)
        b1 = FrozenApprovalBallot(p, name="AppBallot", meta={"metakey": "metavalue"})
        b2 = FrozenApprovalBallot(b1)
        check_members_equality(b1, b2)

        b1 = CardinalBallot({proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"})
        b2 = CardinalBallot(b1)
        check_members_equality(b1, b2)
        b1 = FrozenCardinalBallot({proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"})
        b2 = FrozenCardinalBallot(b1)
        check_members_equality(b1, b2)

        b1 = CumulativeBallot({proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"})
        b2 = CumulativeBallot(b1)
        check_members_equality(b1, b2)
        b1 = FrozenCumulativeBallot({proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"})
        b2 = FrozenCumulativeBallot(b1)
        check_members_equality(b1, b2)

        b1 = OrdinalBallot(p, name="AppBallot", meta={"metakey": "metavalue"})
        b2 = OrdinalBallot(b1)
        check_members_equality(b1, b2)
        b1 = FrozenOrdinalBallot(p, name="AppBallot", meta={"metakey": "metavalue"})
        b2 = FrozenOrdinalBallot(b1)
        check_members_equality(b1, b2)
