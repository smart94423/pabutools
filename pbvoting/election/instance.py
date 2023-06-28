"""
Instances.
"""
from collections.abc import Iterable, Generator
from pbvoting.utils import powerset
from numbers import Number
from math import ceil

import random


class Project:
    """
        A project in a participatory budgeting instance.
        Attributes
        ----------
            name : str, optional
                The name of the project.
                Defaults to `""`
            cost : Number, optional (defaults to `0`)
                The cost of the project.
            categories: set, optional
                set of categories that the project fits into
            targets: set, optional
                set of target groups that the project is targeting
    """

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __init__(self,
                 project_name: str = "",
                 cost: Number = 0,
                 categories=None,
                 targets=None
                 ) -> None:
        if targets is None:
            targets = {}
        if categories is None:
            categories = {}
        self.name = project_name
        self.cost = cost
        self.categories = categories
        self.targets = targets

    def __eq__(self, other):
        if isinstance(other, Project):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other
        return False

    def __le__(self, other):
        if isinstance(other, Project):
            return self.name.__le__(other.name)
        if isinstance(other, str):
            return self.name.__le__(other)

    def __lt__(self, other):
        if isinstance(other, Project):
            return self.name.__lt__(other.name)
        if isinstance(other, str):
            return self.name.__lt__(other)

    def __hash__(self):
        return hash(self.name)


def total_cost(projects: Iterable[Project]) -> Number:
    """
        Returns the total cost of a collection of projects, summing the cost of its content.
        Parameters
        ----------
            projects : iterable of pbvoting.instances.instance.Project
                An iterable of projects.
        Returns
        -------
            Number
                The total cost
    """
    return sum(p.cost for p in projects)


class Instance(set[Project]):
    """
        Participatory Budgeting (PB) instances.
        An instance contains the projects, their cost and the budget limit. Importantly, the profile is not part of
        the instance.
        Note that `PBInstance` is a subclass of `set`, acting as a set of projects.
        Parameters
        ----------
            budget_limit : float
                The budget limit of the instance.
                Defaults to `0.0`.
        Attributes
        ----------
            budget_limit : float, optional
                The budget limit of the instance.
                Defaults to `0.0`.
            categories: set[str], optional
                set of categories that the projects can be assigned to
            targets: set[str], optional
                set of target groups that the project can be targeting
            file_path : str, optional
                If the instance has been parsed from a file, the path to the file. Otherwise, the empty string.
                Defaults to `""`.
            file_name : str, optional
                If the instance has been parsed from a file, the name of the file. Otherwise, the empty string.
                Defaults to `""`.
            parsing_errors : bool, optional
                Boolean indicating if errors were encountered when parsing the file.
            meta : dict of str, optional
                All kinds of relevant information for the instance, stored in a dictionary. Keys and values are
                typically strings.
            project_meta : dict of dict of str, optional
                All kinds of relevant information about the projects, stored in a dictionary. Keys are typically
                strings. Values are dictionary of strings.
        """

    def __init__(self,
                 s: Iterable[Project] = (),
                 budget_limit: float | None = None,
                 categories: set[str] | None = None,
                 targets: set[str] | None = None,
                 file_path: str | None = None,
                 file_name: str | None = None,
                 parsing_errors: bool | None = None,
                 meta: dict | None = None,
                 project_meta: dict | None = None
                 ) -> None:
        super(Instance, self).__init__(s)

        if budget_limit is None:
            if hasattr(s, "budget_limit"):
                budget_limit = s.budget_limit
            else:
                budget_limit = 0.0
        self.budget_limit = budget_limit

        if categories is None:
            if hasattr(s, "categories"):
                categories = s.categories
            else:
                categories = set()
        self.categories = categories

        if targets is None:
            if hasattr(s, "targets"):
                targets = s.targets
            else:
                targets = set()
        self.targets = targets

        if file_path is None:
            if hasattr(s, "file_path"):
                file_path = s.file_path
            else:
                file_path = ""
        self.file_path = file_path

        if file_name is None:
            if hasattr(s, "file_name"):
                file_name = s.file_name
            else:
                file_name = ""
        self.file_name = file_name

        if parsing_errors is None:
            if hasattr(s, "parsing_errors"):
                parsing_errors = s.parsing_errors
            else:
                parsing_errors = False
        self.parsing_errors = parsing_errors

        if meta is None:
            if hasattr(s, "meta"):
                meta = s.meta
            else:
                meta = dict()
        self.meta = meta

        if project_meta is None:
            if hasattr(s, "project_meta"):
                project_meta = s.project_meta
            else:
                project_meta = dict()
        self.project_meta = project_meta

    def get_project(self, project_name: str) -> Project:
        for p in self:
            if p.name == project_name:
                return p
        raise KeyError("No project with name {} found in the instance.".format(project_name))

    def budget_allocations(self) -> Generator[Iterable[Project], None, None]:
        """
            Returns a generator of all the feasible budget allocations of the instance.
            Returns
            -------
                Generator of iterable of projects
        """
        for b in powerset(self):
            if self.is_feasible(b):
                yield b

    def is_trivial(self) -> bool:
        """
            Tests if the instance is trivial, meaning that either all projects can be selected without
            exceeding the budget limit, or that no project can be selected.
            Returns
            -------
                bool
        """
        return (total_cost(self) <= self.budget_limit) or (self.budget_limit <= min([p.cost for p in self]))

    def is_feasible(self, projects: Iterable[Project]) -> bool:
        """
            Tests if a given set of projects is feasible, meaning that its total cost does not exceed the budget
            limit.
            Parameters
            ----------
                projects : iterable of projects
                The set of projects.
            Returns
            -------
                bool
        """
        return total_cost(projects) <= self.budget_limit

    def is_exhaustive(self, projects: Iterable[Project]) -> bool:
        """
            Tests if a given set of projects is exhaustive, meaning that no additional project could be added without
            violating the budget limit. Note that we do not explicitly check for feasibility first.
            Parameters
            ----------
                projects : iterable of projects
                The set of projects.
            Returns
            -------
                bool
        """
        cost = total_cost(projects)
        for p in self:
            if p not in projects and (p.cost + cost <= self.budget_limit):
                return False
        return True

    def __str__(self):
        res = "Instance "
        if self.file_name:
            res += "({}) ".format(self.file_name)
        res += "with budget limit {} and {} projects:\n".format(self.budget_limit, len(self))
        for p in self:
            res += "\tc({}) = {}\n".format(p, p.cost)
        return res[:-1]

    def __repr__(self):
        return self.__str__()

    # This allows set method returning copies of a set to work with PBInstances
    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, set) and not hasattr(result, 'foo'):
                    result = cls(result, budget_limit=self.budget_limit, file_name=self.file_name,
                                 file_path=self.file_path, parsing_errors=self.parsing_errors, meta=self.meta,
                                 project_meta=self.project_meta)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


Instance._wrap_methods(['__ror__', 'difference_update', '__isub__',
                          'symmetric_difference', '__rsub__', '__and__', '__rand__', 'intersection',
                          'difference', '__iand__', 'union', '__ixor__',
                          'symmetric_difference_update', '__or__', 'copy', '__rxor__',
                          'intersection_update', '__xor__', '__ior__', '__sub__',
                        ])


def get_random_instance(num_projects: int, min_cost: int, max_cost: int) -> Instance:
    """
        Generates a random instance. Costs and budget limit are integers. The cost are selected uniformly between
        min_cost and max_cost. The budget limit is sample form a uniform between the minimum cost of a project
        and the total cost of all the projects.
        The parameters are rounded up to the closest int.
        Parameters
        ----------
            num_projects : int
                The number of projects in the instance.
            min_cost : int
                The minimum cost of a project.
            max_cost : int
                The maximum cost of a project.
        Returns
        -------
            pbvoting.instances.instance.PBInstance
    """
    inst = Instance()
    inst.update([Project(project_name=str(p), cost=random.randint(round(min_cost), round(max_cost))) for p in range(
        round(num_projects))])
    inst.budget_limit = random.randint(ceil(min([p.cost for p in inst])), ceil(sum([p.cost for p in inst])))
    return inst
