"""
Module testing the ballots.
"""
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
    AbstractBallot,
    FrozenBallot,
    Ballot,
)
from tests.test_class_inheritence import check_members_equality


class TestBallot(TestCase):
    def test_init_with_ballots(self):
        """
        Test that initialising a ballot with another one works properly.
        """
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
        """
        General tests for approval ballots.
        """
        p1 = Project("p1", 1)
        p2 = Project("p2", 2)
        p3 = Project("p3", 5)
        p4 = Project("p4", 3)
        p5 = Project("p5", 2)
        p6 = Project("p6", 2)
        # Test that the ballot is what is should be
        ballot = ApprovalBallot(
            [p1, p2, p3, p4], name="AppBallot", meta={"metakey": "value"}
        )
        assert p1 in ballot
        assert p2 in ballot
        assert p3 in ballot
        assert p4 in ballot
        assert p5 not in ballot
        assert p6 not in ballot

        # Test that all the ways to define a frozen approval ballot lead to the same
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

        # Test the random generation of approval ballots
        get_random_approval_ballot([p1, p2, p3, p4, p5, p6])

        # Test frozen ballots methods
        hash(frozen_ballot1)

    def test_cardinal_ballot(self):
        """
        General tests for cardinal ballots.
        """
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        # Test that the scores are stored properly
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

        # Test that all the ways to define a frozen approval ballot lead to the same
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

        # Test that frozen ballots are indeed frozen
        with self.assertRaises(ValueError):
            frozen_ballot1[Project("new_proj", 1)] = 76

        # Test completing a cardinal ballot
        ballot.complete(projects, 0.5)
        assert len(ballot) == len(projects)
        for project in projects[6:]:
            assert ballot[project] == 0.5

        # Test frozen ballots methods
        hash(frozen_ballot1)

    def test_cumulative_ballot(self):
        """
        General tests for cumulative ballots.
        """
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        # Test that the scores are stored properly
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

        # Test that all the ways to define a frozen approval ballot lead to the same
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

        # Test that frozen ballots are indeed frozen
        with self.assertRaises(ValueError):
            frozen_ballot1[Project("new_proj", 1)] = 7

        # Test frozen ballots methods
        FrozenCumulativeBallot()
        hash(frozen_ballot1)

    def test_ordinal_ballot(self):
        """
        General tests for ordinal ballots.
        """
        projects = [Project("p" + str(i), cost=2) for i in range(10)]
        # Test that the order is properly stored
        b1 = OrdinalBallot([projects[0], projects[1], projects[2]])
        assert b1 != [projects[0]]
        assert b1 != [projects[0], projects[1], projects[3]]
        assert not b1 == [projects[0]]
        assert not b1 == [projects[0], projects[1], projects[3]]

        # Test initialising an ordinal ballot step by step
        b2 = OrdinalBallot()
        b2.append(projects[0])
        b2.append(projects[1])
        b2.append(projects[2])
        assert b1 == b2

        # Test methods of ordinal ballots
        b1.__repr__()
        b1.__str__()
        with self.assertRaises(ValueError):
            b2.index(Project())
        with self.assertRaises(ValueError):
            b2.at_index(123)

        # Test addition of ordinal ballots
        b3 = b1 + b2
        assert len(b3) == len(b1) == len(b2)
        b3 += OrdinalBallot([projects[5], projects[9]])
        assert len(b3) == 5
        assert b3.at_index(3) == projects[5]
        assert b3.at_index(4) == projects[9]
        with self.assertRaises(TypeError):
            b3 += 123

        # Test reversing order
        b1 = OrdinalBallot([projects[0], projects[1], projects[2]])
        b2 = reversed(b1)
        assert isinstance(b2, OrdinalBallot)
        assert b2 == OrdinalBallot([projects[2], projects[1], projects[0]])

        # Test the arithmetic of ordinal ballots
        o = OrdinalBallot([projects[0], projects[1], projects[2]])
        o1 = OrdinalBallot([projects[0], projects[1]])
        o2 = OrdinalBallot([projects[2], projects[0], projects[1]])
        assert o == o
        assert o <= o
        assert o >= o
        assert o != o1
        assert o1 < o < o2
        assert not o1 > o > o2
        assert o2 > o > o1
        assert not o2 < o < o1
        assert o1 < o2
        assert not o1 > o2
        assert o2 > o1
        assert not o2 < o1
        assert o1 <= o <= o2
        assert not o1 >= o >= o2
        assert o2 >= o >= o1
        assert not o2 <= o <= o1
        assert o1 <= o2
        assert not o1 >= o2
        assert o2 >= o1
        assert not o2 <= o1
        assert o2 != o
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

        # Test all the ways to generate frozen ballots
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

        # Test that we fail if projects are repeated
        with self.assertRaises(ValueError):
            FrozenOrdinalBallot([projects[0], projects[0], projects[2]])

        # Test frozen ballots methods
        hash(frozen_ballot1)

    def test_ballot(self):
        """
        General tests for unspecified ballots.
        """

        # Default of the constructors
        class MyAbstractBallot(AbstractBallot, list):
            pass

        b = MyAbstractBallot()
        assert b.meta == dict()

        class MyFrozenBallot(FrozenBallot, list):
            pass

        b = MyFrozenBallot()
        assert b.meta == dict()

        class MyBallot(Ballot, list):
            def frozen(self) -> FrozenBallot:
                pass

        b = MyBallot()
        assert b.meta == dict()
