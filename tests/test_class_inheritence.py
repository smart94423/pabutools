from copy import deepcopy

from unittest import TestCase

from pbvoting.analysis.instanceproperties import *
from pbvoting.analysis.profileproperties import *
from pbvoting.analysis.votersatisfaction import *
from pbvoting.analysis.category import *
from pbvoting.election import FrozenCardinalBallot, CumulativeBallot

from pbvoting.election.satisfaction import Cost_Sat, Additive_Borda_Sat, Cardinality_Sat
from pbvoting.election.ballot import ApprovalBallot, OrdinalBallot, CardinalBallot
from pbvoting.election.profile import OrdinalProfile
from pbvoting.fractions import frac


class TestAnalysis(TestCase):

    def check_members_equality(self, obj1, obj2):
        assert type(obj1) == type(obj2)
        obj1_attrs = [a for a in dir(obj1) if a[:2] + a[-2:] != '____' and not callable(getattr(obj1, a))]
        obj2_attrs = [a for a in dir(obj2) if a[:2] + a[-2:] != '____' and not callable(getattr(obj2, a))]
        assert obj1_attrs == obj2_attrs
        for attr in obj1_attrs:
            assert obj1.__getattribute__(attr) == obj2.__getattribute__(attr)

    def check_set_members(self, set_class, initial_set, included_objects, additional_objects):
        new_set = deepcopy(initial_set)

        new_set.add(additional_objects[0])
        self.check_members_equality(initial_set, new_set)

        new_set.discard(included_objects[0])
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set.remove(included_objects[0])
        self.check_members_equality(initial_set, new_set)

        new_set.clear()
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set.pop()
        self.check_members_equality(initial_set, new_set)

        new_set = initial_set.copy()
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set = new_set.difference(set_class(additional_objects))
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set.difference_update(set_class(additional_objects))
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set = new_set.intersection(set_class(additional_objects), set_class(additional_objects))
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set = new_set.symmetric_difference(set_class(additional_objects))
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set.symmetric_difference_update(set_class(additional_objects))
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set = new_set.union(set_class(additional_objects))
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set.update(set_class(additional_objects))
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set = new_set.__ior__(initial_set)
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set = new_set | initial_set
        self.check_members_equality(initial_set, new_set)

        new_set = deepcopy(initial_set)
        new_set |= initial_set
        self.check_members_equality(initial_set, new_set)

    def test_instance_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        instance = Instance(projects[:10], budget_limit=10, categories={"cat1", "cat2"}, targets={"targ1", "targ2"},
                            file_path="filepath", file_name="filename", parsing_errors=True,
                            meta={"metakey": "metavalue"},
                            project_meta={p: {"proj_metakey", "proje_metavalue"} for p in projects[:10]})
        self.check_set_members(Instance, instance, projects[:10], projects[10:])

    def test_approvalballots_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        ballot = ApprovalBallot(projects[:10], name="sqdkj", meta={"fd": "fsdfb"})
        self.check_set_members(ApprovalBallot, ballot, projects[:10], projects[10:])

    def check_dict_members(self, initial_dict, included_keys, additional_keys):
        new_dict = deepcopy(initial_dict)

        new_dict.clear()
        self.check_members_equality(initial_dict, new_dict)

        new_dict = initial_dict.copy()
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.get(included_keys[0])
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.items()
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.keys()
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.pop(included_keys[0])
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.popitem()
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.setdefault(included_keys[0])
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.setdefault(additional_keys[0])
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.update({k: 10 for k in additional_keys})
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict.values()
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict = new_dict.__ior__(initial_dict)
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict = new_dict | initial_dict
        self.check_members_equality(initial_dict, new_dict)

        new_dict = deepcopy(initial_dict)
        new_dict |= initial_dict
        self.check_members_equality(initial_dict, new_dict)

    def test_dictballots_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        scores = {p: 4 for p in projects[:10]}
        # ballot = FrozenCardinalBallot(scores, name="sqdkj", meta={"fd": "fsdfb"})
        # self.check_dict_members(ballot, projects[:10], projects[10:])
        ballot = CardinalBallot(scores, name="nameoftheballot", meta={"metakey": "metavalue"})
        self.check_dict_members(ballot, projects[:10], projects[10:])
        ballot = CumulativeBallot(scores, name="nameoftheballot", meta={"metakey": "metavalue"})
        self.check_dict_members(ballot, projects[:10], projects[10:])
        ballot = OrdinalBallot(projects[:10], name="nameoftheballot", meta={"metakey": "metavalue"})
        self.check_dict_members(ballot, projects[:10], projects[10:])

    def check_list_members(self, initial_list, included_objects, additional_objects):
        new_list = deepcopy(initial_list)

        new_list.clear()
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.append(additional_objects[0])
        self.check_members_equality(initial_list, new_list)

        new_list = initial_list.copy()
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.count(included_objects[0])
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.extend(additional_objects)
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.index(included_objects[0])
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.insert(3, additional_objects[0])
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.pop()
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.remove(included_objects[0])
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list.reverse()
        self.check_members_equality(initial_list, new_list)

        try:
            new_list = deepcopy(initial_list)
            new_list.sort()
            self.check_members_equality(initial_list, new_list)
        except NotImplementedError:
            pass

        new_list = deepcopy(initial_list)
        new_list += new_list
        self.check_members_equality(initial_list, new_list)

        new_list = deepcopy(initial_list)
        new_list *= 5
        self.check_members_equality(initial_list, new_list)

    def test_profile_members(self):
        projects = [Project(str(i), i) for i in range(20)]
        instance = Instance(projects)
        ballots = [ApprovalBallot(projects, name="app" + str(i), meta={"key" + str(i): "v"}) for i in range(20)]
        profile = ApprovalProfile(ballots[:10],
                                  instance=instance,
                                  ballot_validation=False,
                                  ballot_type=CumulativeBallot,
                                  legal_min_length=10,
                                  legal_max_length=100,
                                  legal_min_cost=2100,
                                  legal_max_cost=15)
        self.check_list_members(profile, ballots[:10], ballots[10:])

        ballots = [CardinalBallot({p: 5 for p in projects}, name="app" + str(i), meta={"key" + str(i): "v"})
                   for i in range(20)]
        profile = CardinalProfile(ballots[:10],
                                  instance=instance,
                                  ballot_validation=False,
                                  ballot_type=CumulativeBallot,
                                  legal_min_length=10,
                                  legal_max_length=100,
                                  legal_min_score=1000,
                                  legal_max_score=555)
        self.check_list_members(profile, ballots[:10], ballots[10:])

        ballots = [CumulativeBallot({p: 5 for p in projects}, name="app" + str(i), meta={"key" + str(i): "v"})
                   for i in range(20)]
        profile = CumulativeProfile(ballots[:10],
                                    instance=instance,
                                    ballot_validation=False,
                                    ballot_type=CumulativeBallot,
                                    legal_min_length=105,
                                    legal_max_length=120,
                                    legal_min_score=1020,
                                    legal_max_score=535,
                                    legal_min_total_score=87,
                                    legal_max_total_score=45)
        self.check_list_members(profile, ballots[:10], ballots[10:])

        ballots = [OrdinalBallot(projects, name="app" + str(i), meta={"key" + str(i): "v"}) for i in range(20)]
        profile = OrdinalProfile(ballots[:10],
                                 instance=instance,
                                 ballot_validation=False,
                                 ballot_type=CumulativeBallot,
                                 legal_min_length=10,
                                 legal_max_length=100)
        self.check_list_members(profile, ballots[:10], ballots[10:])
