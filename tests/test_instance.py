from unittest import TestCase
from pabutools.election.instance import *


class TestInstance(TestCase):
    def test_instance(self):
        inst = Instance(
            [Project("p1", 2), Project("p2", 1), Project("p3", 1)], budget_limit=2
        )
        assert inst.budget_limit == 2
        assert len(inst) == 3

        inst.file_name = "file"
        inst.__str__()
        inst.__repr__()

        with self.assertRaises(KeyError):
            inst.get_project("name_that_does_not_appear")

        p1 = inst.get_project("p1")
        assert p1.name == "p1"
        assert p1.cost == 2
        assert inst.is_trivial() is False
        budget_allocations = []
        for budget_allocation in inst.budget_allocations():
            budget_allocations.append(budget_allocation)
        assert len(budget_allocations) == 5
        assert (
            inst.is_feasible([Project("p1", 2), Project("p2", 1), Project("p3", 1)])
            is False
        )
        assert inst.is_feasible([Project("p1", 2)]) is True
        assert (
            inst.is_exhaustive([Project("p1", 2), Project("p2", 1), Project("p3", 1)])
            is True
        )
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
        inst2 = Instance(inst)
        assert inst2.budget_limit == inst.budget_limit
        assert inst2.categories == inst.categories
        assert inst2.targets == inst.targets
        assert inst2.file_path == inst.file_path
        assert inst2.file_name == inst.file_name
        assert inst2.parsing_errors == inst.parsing_errors
        assert inst2.meta == inst.meta
        assert inst2.project_meta == inst.project_meta

    def test_projects(self):
        projects = [Project("p{}".format(i), (i + 1) * 2) for i in range(10)]
        assert total_cost(projects) == 110
        assert max_budget_allocation_cardinality(projects, budget_limit=30) == 5
        assert max_budget_allocation_cost(projects, budget_limit=29) == 28
        project = Project("p", 10)
        assert project == Project("p", 2)
        assert project == "p"
        project.__str__()
        project.__repr__()
        assert not project == Instance()
        assert project <= "p"
        assert project <= Project("z")
        assert project < "z"
        assert project < Project("z")

        project = Project("test", 2.0)
        assert isinstance(project.cost, int)
        project = Project("test", 2.5)
        assert not isinstance(project.cost, float)
