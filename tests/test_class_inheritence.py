"""
Module testing class inheritance for basic Python classes (list, tuple, etc...).
"""
from copy import deepcopy

from unittest import TestCase

from pabutools.election import (
    Instance,
    Project,
    ApprovalBallot,
    ApprovalProfile,
    OrdinalBallot,
    OrdinalProfile,
    CardinalBallot,
    CardinalProfile,
    CumulativeBallot,
    CumulativeProfile,
    SatisfactionProfile,
    Additive_Borda_Sat,
    ApprovalMultiProfile,
    FrozenApprovalBallot,
    FrozenCumulativeBallot,
    FrozenCardinalBallot,
    CardinalMultiProfile,
    CumulativeMultiProfile,
    FrozenOrdinalBallot,
    OrdinalMultiProfile,
    SatisfactionMultiProfile,
)


def check_members_equality(obj1, obj2, verbose=False):
    assert type(obj1) == type(obj2)
    obj1_attrs = [
        a
        for a in dir(obj1)
        if a[:2] + a[-2:] != "____" and not callable(getattr(obj1, a))
    ]
    obj2_attrs = [
        a
        for a in dir(obj2)
        if a[:2] + a[-2:] != "____" and not callable(getattr(obj2, a))
    ]
    if verbose:
        print(f"{obj1_attrs}     {obj2_attrs}")
    assert obj1_attrs == obj2_attrs
    for attr in obj1_attrs:
        if verbose:
            print(
                f"{attr} : {obj1.__getattribute__(attr)}    {obj2.__getattribute__(attr)}"
            )
        assert obj1.__getattribute__(attr) == obj2.__getattribute__(attr)


def check_set_members(set_class, initial_set, included_objects, additional_objects):
    new_set = deepcopy(initial_set)
    check_members_equality(initial_set, new_set)

    new_set.add(additional_objects[0])
    check_members_equality(initial_set, new_set)

    new_set.discard(included_objects[0])
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set.remove(included_objects[0])
    check_members_equality(initial_set, new_set)

    new_set.clear()
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set.pop()
    check_members_equality(initial_set, new_set)

    new_set = initial_set.copy()
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set = new_set.difference(set_class(additional_objects))
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set.difference_update(set_class(additional_objects))
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set = new_set.intersection(
        set_class(additional_objects), set_class(additional_objects)
    )
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set = new_set.symmetric_difference(set_class(additional_objects))
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set.symmetric_difference_update(set_class(additional_objects))
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set = new_set.union(set_class(additional_objects))
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set.update(set_class(additional_objects))
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set = new_set.__ior__(initial_set)
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set = new_set | initial_set
    check_members_equality(initial_set, new_set)

    new_set = deepcopy(initial_set)
    new_set |= initial_set
    check_members_equality(initial_set, new_set)


def check_dict_members(initial_dict, included_keys, additional_keys):
    new_dict = deepcopy(initial_dict)
    check_members_equality(initial_dict, new_dict)

    new_dict.clear()
    check_members_equality(initial_dict, new_dict)

    new_dict = initial_dict.copy()
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.get(included_keys[0])
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.items()
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.keys()
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.pop(included_keys[0])
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.popitem()
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.setdefault(included_keys[0])
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.setdefault(additional_keys[0])
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.update({k: 10 for k in additional_keys})
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict.values()
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict = new_dict.__ior__(initial_dict)
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict = new_dict | initial_dict
    check_members_equality(initial_dict, new_dict)

    new_dict = deepcopy(initial_dict)
    new_dict |= initial_dict
    check_members_equality(initial_dict, new_dict)


def check_list_members(initial_list, included_objects, additional_objects):
    new_list = deepcopy(initial_list)
    check_members_equality(initial_list, new_list)

    new_list.clear()
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.append(additional_objects[0])
    check_members_equality(initial_list, new_list)

    new_list = initial_list.copy()
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.count(included_objects[0])
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.extend(additional_objects)
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.index(included_objects[0])
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.insert(3, additional_objects[0])
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.pop()
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.remove(included_objects[0])
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list.reverse()
    check_members_equality(initial_list, new_list)

    try:
        new_list = deepcopy(initial_list)
        new_list.sort()
        check_members_equality(initial_list, new_list)
    except NotImplementedError:
        pass

    new_list = deepcopy(initial_list)
    new_list += new_list
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list *= 5
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list = new_list[1:5]
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list = new_list[:-1]
    check_members_equality(initial_list, new_list)

    new_list = deepcopy(initial_list)
    new_list = new_list[0:5:2]
    check_members_equality(initial_list, new_list)


class TestAnalysis(TestCase):
    def test_instance_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        instance = Instance(
            projects[:10],
            budget_limit=10,
            categories={"cat1", "cat2"},
            targets={"targ1", "targ2"},
            file_path="filepath",
            file_name="filename",
            parsing_errors=True,
            meta={"metakey": "metavalue"},
            project_meta={
                p: {"proj_metakey", "proje_metavalue"} for p in projects[:10]
            },
        )
        check_set_members(Instance, instance, projects[:10], projects[10:])

    def test_approvalballots_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        ballot = ApprovalBallot(projects[:10], name="sqdkj", meta={"fd": "fsdfb"})
        check_set_members(ApprovalBallot, ballot, projects[:10], projects[10:])

    def test_dictballots_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        scores = {p: 4 for p in projects[:10]}
        # ballot = FrozenCardinalBallot(scores, name="sqdkj", meta={"fd": "fsdfb"})
        # self.check_dict_members(ballot, projects[:10], projects[10:])
        ballot = CardinalBallot(
            scores, name="nameoftheballot", meta={"metakey": "metavalue"}
        )
        check_dict_members(ballot, projects[:10], projects[10:])
        ballot = CumulativeBallot(
            scores, name="nameoftheballot", meta={"metakey": "metavalue"}
        )
        check_dict_members(ballot, projects[:10], projects[10:])
        ballot = OrdinalBallot(
            projects[:10], name="nameoftheballot", meta={"metakey": "metavalue"}
        )
        check_dict_members(ballot, projects[:10], projects[10:])

    def test_profile_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        instance = Instance(projects)
        ballots = [
            ApprovalBallot(projects, name="app" + str(i), meta={"key" + str(i): "v"})
            for i in range(20)
        ]
        profile = ApprovalProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=CumulativeBallot,
            legal_min_length=10,
            legal_max_length=100,
            legal_min_cost=2100,
            legal_max_cost=15,
        )
        check_list_members(profile, ballots[:10], ballots[10:])

        ballots = [
            CardinalBallot(
                {p: 5 for p in projects},
                name="app" + str(i),
                meta={"key" + str(i): "v"},
            )
            for i in range(20)
        ]
        profile = CardinalProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=CumulativeBallot,
            legal_min_length=10,
            legal_max_length=100,
            legal_min_score=1000,
            legal_max_score=555,
        )
        check_list_members(profile, ballots[:10], ballots[10:])

        ballots = [
            CumulativeBallot(
                {p: 5 for p in projects},
                name="app" + str(i),
                meta={"key" + str(i): "v"},
            )
            for i in range(20)
        ]
        profile = CumulativeProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=CumulativeBallot,
            legal_min_length=105,
            legal_max_length=120,
            legal_min_score=1020,
            legal_max_score=535,
            legal_min_total_score=87,
            legal_max_total_score=45,
        )
        check_list_members(profile, ballots[:10], ballots[10:])

        ballots = [
            OrdinalBallot(projects, name="app" + str(i), meta={"key" + str(i): "v"})
            for i in range(20)
        ]
        profile = OrdinalProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=CumulativeBallot,
            legal_min_length=10,
            legal_max_length=100,
        )
        check_list_members(profile, ballots[:10], ballots[10:])

        sat_profile = SatisfactionProfile(
            instance=instance, profile=profile, sat_class=Additive_Borda_Sat
        )
        sats = [Additive_Borda_Sat(instance, profile, ballot) for ballot in ballots]
        check_list_members(sat_profile, sats[:10], sats[10:])

    def test_multiprofile_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        instance = Instance(projects)
        ballots = [
            FrozenApprovalBallot(
                projects, name="app" + str(i), meta={"key" + str(i): "v"}
            )
            for i in range(20)
        ]
        profile = ApprovalMultiProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=FrozenCumulativeBallot,
            legal_min_length=10,
            legal_max_length=100,
            legal_min_cost=2100,
            legal_max_cost=15,
        )
        check_dict_members(profile, ballots[:10], ballots[10:])

        ballots = [
            FrozenCardinalBallot(
                {p: 5 for p in projects},
                name="app" + str(i),
                meta={"key" + str(i): "v"},
            )
            for i in range(20)
        ]
        profile = CardinalMultiProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=CumulativeBallot,
            legal_min_length=10,
            legal_max_length=100,
            legal_min_score=1000,
            legal_max_score=555,
        )
        # check_dict_members(profile, ballots[:10], ballots[10:])

        ballots = [
            FrozenCumulativeBallot(
                {p: 5 for p in projects},
                name="app" + str(i),
                meta={"key" + str(i): "v"},
            )
            for i in range(20)
        ]
        profile = CumulativeMultiProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=CumulativeBallot,
            legal_min_length=105,
            legal_max_length=120,
            legal_min_score=1020,
            legal_max_score=535,
            legal_min_total_score=87,
            legal_max_total_score=45,
        )
        # check_dict_members(profile, ballots[:10], ballots[10:])

        ballots = [
            FrozenOrdinalBallot(
                projects, name="app" + str(i), meta={"key" + str(i): "v"}
            )
            for i in range(20)
        ]
        profile = OrdinalMultiProfile(
            ballots[:10],
            instance=instance,
            ballot_validation=False,
            ballot_type=CumulativeBallot,
            legal_min_length=10,
            legal_max_length=100,
        )
        check_dict_members(profile, ballots[:10], ballots[10:])

        sat_profile = SatisfactionMultiProfile(
            instance=instance, multiprofile=profile, sat_class=Additive_Borda_Sat
        )
        sats = [Additive_Borda_Sat(instance, profile, ballot) for ballot in ballots]
        check_dict_members(sat_profile, sats[:10], sats[10:])
