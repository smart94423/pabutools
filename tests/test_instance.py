from unittest import TestCase
from pbvoting.instance.pbinstance import *


class TestInstance(TestCase):
    def test_instance_as_set(self):
        inst = PBInstance()
        projects = [Project("p{}".format(i), 1) for i in range(10)]
        inst.add(projects[0])
        assert len(inst) == 1
        inst.add(projects[1])
        assert len(inst) == 2
        inst.update(projects[:7])
        assert len(inst) == 7
        inst.file_name = "File_Name"
        inst.__str__()
        inst.__repr__()

        inst2 = PBInstance()
        inst2.update(projects)
        inst3 = inst.union(inst2)
        assert len(inst3) == 10
        assert type(inst3) == PBInstance

    def test_instance(self):
        inst = PBInstance([Project("p1", 2), Project("p2", 1), Project("p3", 1)], budget_limit=2)
        assert inst.budget_limit == 2
        assert len(inst) == 3
        try:
            inst.get_project("name_that_does_not_appear")
        except KeyError:
            pass
        p1 = inst.get_project("p1")
        assert p1.name == "p1"
        assert p1.cost == 2
        assert inst.is_trivial() is False
        budget_allocations = []
        for budget_allocation in inst.budget_allocations():
            budget_allocations.append(budget_allocation)
        assert len(budget_allocations) == 5
        assert inst.is_feasible([Project("p1", 2), Project("p2", 1), Project("p3", 1)]) is False
        assert inst.is_feasible([Project("p1", 2)]) is True
        assert inst.is_exhaustive([Project("p1", 2), Project("p2", 1), Project("p3", 1)]) is True
        assert inst.is_exhaustive([Project("p2", 1)]) is False
        assert inst.is_exhaustive([Project("p3", 1)]) is False
        inst = get_random_instance(10, 1, 10)
        assert len(inst) == 10
        inst = get_random_instance(10.4, 1.1, 10.8)
        assert len(inst) == 10
        inst = get_random_instance(10.9, 1.1, 10.8)
        assert len(inst) == 11

        inst.categories = {"Cat1", "Cat2", "Cat3"}
        inst.targets = {"Targ1", "Targ2", "Targ3"}
        inst.file_path = "path"
        inst.file_name = "name"
        inst.parsing_errors = False
        inst2 = PBInstance(inst)
        assert inst2.budget_limit == inst.budget_limit
        assert inst2.categories == inst.categories
        assert inst2.targets == inst.targets
        assert inst2.file_path == inst.file_path
        assert inst2.file_name == inst.file_name
        assert inst2.parsing_errors == inst.parsing_errors
        assert inst2.meta == inst.meta
        assert inst2.project_meta == inst.project_meta

        inst3 = inst.copy()
        assert inst3 == inst

    def test_projects(self):
        projects = [Project("p{}".format(i), 1) for i in range(10)]
        assert total_cost(projects) == 10
        project = Project("p", 10)
        assert project == Project("p", 2)
        assert project == "p"
        project.__str__()
        project.__repr__()
        assert not project == PBInstance()
        assert project <= "p"
        assert project <= Project("z")
        assert project < "z"
        assert project < Project("z")

