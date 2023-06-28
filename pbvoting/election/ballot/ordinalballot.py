from collections.abc import Iterable

from pbvoting.election.ballot.ballot import FrozenBallot, Ballot
from pbvoting.election.instance import Project


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
