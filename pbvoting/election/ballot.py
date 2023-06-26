import random

from collections.abc import Iterable
from fractions import Fraction

from pbvoting.election import Project

class Ballot:
    """
        A ballot.
        This is the class that all ballot formats inherit from.
        Attributes
        ----------
            name : str
                The identifier of the ballot.
                Defaults to `""`
            meta : dict (of str)
                Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
                strings. Could for instance store the gender of the voter, their location etc...
    """

    def __init__(self, name: str = "", meta: dict | None = None):
        if meta is None:
            meta = dict()
        self.meta = meta
        self.name = name

    def freeze(self):
        pass



class ApprovalBallot(set[Project], Ballot):
    """
        An approval ballot, that is, a ballot in which the voter has indicated the projects that they approve of. It
        is a subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
    """

    def __init__(self,
                 approved: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        set.__init__(self, approved)
        Ballot.__init__(self, name, meta)

    def freeze(self):
        return FrozenApprovalBallot(self, name=self.name, meta=self.meta)

    # This allows set method returning copies of a set to work with PBInstances
    # See https://stackoverflow.com/questions/798442/what-is-the-correct-or-best-way-to-subclass-the-python-set-class-adding-a-new
    @classmethod
    def _wrap_methods(cls, methods):
        def wrap_method_closure(method):
            def inner_method(self, *args):
                result = getattr(super(cls, self), method)(*args)
                if isinstance(result, set) and not hasattr(result, 'name'):
                    result = cls(approved=result, name=self.name, meta=self.meta)
                return result

            inner_method.fn_name = method
            setattr(cls, method, inner_method)

        for m in methods:
            wrap_method_closure(m)


ApprovalBallot._wrap_methods(['__ror__', 'difference_update', '__isub__',
                              'symmetric_difference', '__rsub__', '__and__', '__rand__', 'intersection',
                              'difference', '__iand__', 'union', '__ixor__',
                              'symmetric_difference_update', '__or__', 'copy', '__rxor__',
                              'intersection_update', '__xor__', '__ior__', '__sub__',
                              ])

def get_random_approval_ballot(projects: Iterable[Project], name: str = "RandomAppBallot") -> ApprovalBallot:
    """
        Generates a random approval ballot in which each project is approved with probability 0.5.
        Parameters
        ----------
            projects : collection of pbvoting.instance.instance.Project
                The set of all the projects.
            name : str
                The identifier of the ballot. Default is `"RandomAppBallot"`.
        Returns
        -------
            pbvoting.instance.profile.ApprovalBallot
    """
    ballot = ApprovalBallot(name=name)
    for p in projects:
        if random.random() > 0.5:
            ballot.add(p)
    return ballot


class CardinalBallot(dict[Project, Fraction], Ballot):
    """
        A cardinal ballot, that is, a ballot in which the voter has indicated a score for every project. It is a
        subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
            d : dict of projects: score
                The score assigned to the projects. The keys are the projects and map to the score.
                Defaults to the empty dictionary.
    """

    def __init__(self,
                 d: dict[Project, Fraction] = None,
                 name: str = "",
                 meta: dict | None = None):
        if d is None:
            d = {}
        dict.__init__(self, d)
        Ballot.__init__(self, name=name, meta=meta)

    def complete(self, projects, default_score):
        for project in projects:
            if project not in self:
                self[project] = default_score

    def freeze(self):
        return FrozenCardinalBallot(self)



class CumulativeBallot(CardinalBallot):
    """
        A cumulative ballot, that is, a ballot in which the voter has indicated a score for every project using a
        total number of points allocated to the voter. It is a subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
            iterable : dict of projects: score
                The score assigned to the projects. The keys are the projects and map to the score.
                Defaults to the empty dictionary.
    """

    def __init__(self,
                 d: dict[Project, Fraction] = None,
                 name: str = "",
                 meta: dict | None = None):
        if d is None:
            d = {}
        dict.__init__(self, d)
        CardinalBallot.__init__(self, name=name, meta=meta)


class OrdinalBallot(dict, Ballot):

    def __init__(self,
                 iterable: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        dict.__init__(self, {e: None for e in iterable})
        Ballot.__init__(self, name=name, meta=meta)

    def append(self, element):
        self[element] = None

    def __add__(self, other):
        result = OrdinalBallot(self, name=self.name, meta=self.meta)
        for e in other:
            result[e] = None
        return result

    def index(self, element):
        i = 0
        for e in self:
            if e == element:
                return i
            i += 1
        raise ValueError("{} is not in the ballot".format(element))

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for e1, e2 in zip(self, other):
            if e1 != e2:
                return False
        return True

    def __repr__(self):
        return list(self.keys()).__repr__()

    def __str__(self):
        return list(self.keys()).__str__()


class FrozenBallot:
    """
    """

    def __init__(self, name: str = "", meta: dict | None = None):
        if meta is None:
            meta = dict()
        self.meta = meta
        self.name = name


class FrozenApprovalBallot(tuple[Project], FrozenBallot):

    def __init__(self,
                 approved: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        tuple.__init__(self)
        FrozenBallot.__init__(self, name, meta)

    def __new__(cls,
                approved: Iterable[Project] = (),
                name: str = "",
                meta: dict | None = None):
        return super(FrozenApprovalBallot, cls).__new__(cls, tuple(approved))

    def __hash__(self):
        return tuple.__hash__(self)



class FrozenCardinalBallot(dict[Project, Fraction], FrozenBallot):

    def __init__(self,
                 d: dict[Project, Fraction] = (),
                 name: str = "",
                 meta: dict | None = None):
        dict.__init__(self, d)
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))



class FrozenCumulativeBallot(dict[Project, Fraction], FrozenBallot):

    def __init__(self,
                 d: dict[Project, Fraction] = (),
                 name: str = "",
                 meta: dict | None = None):
        dict.__init__(self, d)
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))

class FrozenOrdinalBallot(tuple[Project], FrozenBallot):

    def __init__(self,
                 approved: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        tuple.__init__(self)
        FrozenBallot.__init__(self, name, meta)

    def __new__(cls,
                approved: Iterable[Project] = (),
                name: str = "",
                meta: dict | None = None):
        if len(set(approved)) != len(approved):
            raise ValueError("Some projects are repeated in {}, this is not a valid ordinal ballot.".format(approved))
        return super(FrozenOrdinalBallot, cls).__new__(cls, tuple(approved))

    def __hash__(self):
        return tuple.__hash__(self)

