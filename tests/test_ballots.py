from unittest import TestCase

from pabutools.election import (
    Project,
    ApprovalBallot,
    CardinalBallot,
    CumulativeBallot,
    OrdinalBallot,
    FrozenApprovalBallot,
    FrozenCardinalBallot,
    FrozenCumulativeBallot,
    FrozenOrdinalBallot,
    get_random_approval_ballot,
)
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

        b1 = CardinalBallot(
            {proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"}
        )
        b2 = CardinalBallot(b1)
        check_members_equality(b1, b2)
        b1 = FrozenCardinalBallot(
            {proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"}
        )
        b2 = FrozenCardinalBallot(b1)
        check_members_equality(b1, b2)

        b1 = CumulativeBallot(
            {proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"}
        )
        b2 = CumulativeBallot(b1)
        check_members_equality(b1, b2)
        b1 = FrozenCumulativeBallot(
            {proj: 59 for proj in p}, name="CardBallot", meta={"metakey": "metavalue"}
        )
        b2 = FrozenCumulativeBallot(b1)
        check_members_equality(b1, b2)

        b1 = OrdinalBallot(p, name="AppBallot", meta={"metakey": "metavalue"})
        b2 = OrdinalBallot(b1)
        check_members_equality(b1, b2)
        b1 = FrozenOrdinalBallot(p, name="AppBallot", meta={"metakey": "metavalue"})
        b2 = FrozenOrdinalBallot(b1)
        check_members_equality(b1, b2)

    def test_approval_ballot(self):
        p1 = Project("p1", 1)
        p2 = Project("p2", 2)
        p3 = Project("p3", 5)
        p4 = Project("p4", 3)
        p5 = Project("p5", 2)
        p6 = Project("p6", 2)
        ballot = ApprovalBallot(
            [p1, p2, p3, p4], name="AppBallot", meta={"metakey": "value"}
        )
        assert p1 in ballot
        assert p2 in ballot
        assert p3 in ballot
        assert p4 in ballot
        assert p5 not in ballot
        assert p6 not in ballot

        frozen_ballot1 = FrozenApprovalBallot([p1, p2, p3, p4])
        frozen_ballot2 = ballot.frozen()
        frozen_ballot3 = FrozenApprovalBallot(ballot)
        assert (
            set(ballot)
            == set(frozen_ballot1)
            == set(frozen_ballot2)
            == set(frozen_ballot3)
        )
        assert ballot.name == frozen_ballot2.name == frozen_ballot3.name
        assert ballot.meta == frozen_ballot2.meta == frozen_ballot3.meta

        get_random_approval_ballot([p1, p2, p3, p4, p5, p6])

    def test_cardinal_ballot(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        ballot = CardinalBallot(
            {
                projects[1]: 100,
                projects[2]: 74,
                projects[3]: 12,
                projects[4]: 7,
                projects[5]: -41,
            },
            name="CardBallot",
            meta={"MetaKey": "Value"},
        )
        assert ballot[projects[1]] == 100
        assert ballot[projects[2]] == 74
        assert ballot[projects[3]] == 12
        assert ballot[projects[4]] == 7
        assert ballot[projects[5]] == -41

        frozen_ballot1 = FrozenCardinalBallot(
            {
                projects[1]: 100,
                projects[2]: 74,
                projects[3]: 12,
                projects[4]: 7,
                projects[5]: -41,
            }
        )
        frozen_ballot2 = ballot.frozen()
        frozen_ballot3 = FrozenCardinalBallot(ballot)
        for p in ballot:
            assert (
                ballot[p] == frozen_ballot1[p] == frozen_ballot2[p] == frozen_ballot3[p]
            )
        assert ballot.name == frozen_ballot2.name == frozen_ballot3.name
        assert ballot.meta == frozen_ballot2.meta == frozen_ballot3.meta

    def test_cumulative_ballot(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        ballot = CumulativeBallot(
            {
                projects[1]: 4,
                projects[2]: 5,
                projects[3]: 7,
                projects[4]: 57,
                projects[5]: -41,
            },
            name="CumBallot",
            meta={"MetaKey": "Value"},
        )
        assert ballot[projects[1]] == 4
        assert ballot[projects[2]] == 5
        assert ballot[projects[3]] == 7
        assert ballot[projects[4]] == 57
        assert ballot[projects[5]] == -41

        frozen_ballot1 = FrozenCumulativeBallot(
            {
                projects[1]: 4,
                projects[2]: 5,
                projects[3]: 7,
                projects[4]: 57,
                projects[5]: -41,
            }
        )
        frozen_ballot2 = ballot.frozen()
        frozen_ballot3 = FrozenCumulativeBallot(ballot)
        for p in ballot:
            assert (
                ballot[p] == frozen_ballot1[p] == frozen_ballot2[p] == frozen_ballot3[p]
            )
        assert ballot.name == frozen_ballot2.name == frozen_ballot3.name
        assert ballot.meta == frozen_ballot2.meta == frozen_ballot3.meta

    def test_ordinal_ballot(self):
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        b1 = OrdinalBallot([projects[0], projects[1], projects[2]])
        b1.__repr__()
        b1.__str__()
        b2 = OrdinalBallot()
        b2.append(projects[0])
        b2.append(projects[1])
        b2.append(projects[2])
        assert b1 == b2
        b3 = OrdinalBallot(name="Name")
        assert b3.name == "Name"
        b3 += b1
        assert b3 == b1 == b2
        assert b3.name == "Name"

        assert b1 != [projects[0]]
        assert b1 != [projects[0], projects[1], projects[3]]
        assert not b1 == [projects[0]]
        assert not b1 == [projects[0], projects[1], projects[3]]

        with self.assertRaises(ValueError):
            b3.index(123)

        b1 = OrdinalBallot([projects[0], projects[1], projects[2]])
        b2 = reversed(b1)
        assert isinstance(b2, OrdinalBallot)
        assert b2 == OrdinalBallot([projects[2], projects[1], projects[0]])

        o = OrdinalBallot([projects[0], projects[1], projects[2]])
        o1 = OrdinalBallot([projects[0], projects[1]])
        o2 = OrdinalBallot([projects[2], projects[0], projects[1]])
        assert o == o
        assert o <= o
        assert o >= o
        assert o != o1
        assert o1 < o
        assert o1 < o
        assert o1 <= o2
        assert o1 <= o2
        assert o2 != o
        assert o2 > o
        assert o2 >= o
        with self.assertRaises(TypeError):
            o += 1
        with self.assertRaises(TypeError):
            o > 2
        with self.assertRaises(TypeError):
            o < 2
        with self.assertRaises(TypeError):
            o >= 2
        with self.assertRaises(TypeError):
            o <= 2

        ballot = OrdinalBallot(projects, name="OrdBallot", meta={"metakey": "value"})

        frozen_ballot1 = FrozenOrdinalBallot(projects)
        frozen_ballot2 = ballot.frozen()
        frozen_ballot3 = FrozenOrdinalBallot(ballot)
        assert (
            list(ballot)
            == list(frozen_ballot1)
            == list(frozen_ballot2)
            == list(frozen_ballot3)
        )
        assert ballot.name == frozen_ballot2.name == frozen_ballot3.name
        assert ballot.meta == frozen_ballot2.meta == frozen_ballot3.meta
