
from pbvoting.instance.pbinstance import *


def test_instance_as_set():
    inst = PBInstance()
    projects = [Project("p{}".format(i), 1) for i in range(10)]
    inst.add(projects[0])
    assert len(inst) == 1
    inst.add(projects[1])
    assert len(inst) == 2
    inst.update(projects[:7])
    assert len(inst) == 7

    inst2 = PBInstance()
    inst2.update(projects)
    inst3 = inst.union(inst2)
    assert len(inst3) == 10
    assert type(inst3) == PBInstance


def test_instance():
    inst = PBInstance([Project("p1", 2), Project("p2", 1), Project("p3", 1)], budget_limit=2)
    assert inst.budget_limit == 2
    assert len(inst) == 3
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


def test_projects():
    projects = [Project("p{}".format(i), 1) for i in range(10)]
    assert total_cost(projects) == 10
    project = Project("p", 10)
    assert project == Project("p", 2)
    assert project == "p"


if __name__ == "__main__":
    test_instance_as_set()
    test_instance()
    test_projects()