from collections.abc import Iterable

from pabutools.election.ballot.ballot import FrozenBallot, Ballot
from pabutools.election.instance import Project


class FrozenOrdinalBallot(tuple[Project], FrozenBallot):
    def __init__(
        self,
        iterable: Iterable[Project] = (),
        name: str | None = None,
        meta: dict | None = None,
    ) -> None:
        tuple.__init__(self)
        if name is None:
            if hasattr(iterable, "name"):
                name = iterable.name
            else:
                name = ""
        if meta is None:
            if hasattr(iterable, "meta"):
                meta = iterable.meta
            else:
                meta = dict()
        FrozenBallot.__init__(self, name, meta)

    def __new__(
        cls, iterable: Iterable[Project] = (), name: str = "", meta: dict | None = None
    ):
        if len(set(iterable)) != len(iterable):
            raise ValueError(
                "Some projects are repeated in {}, this is not a valid ordinal ballot.".format(
                    iterable
                )
            )
        return super(FrozenOrdinalBallot, cls).__new__(cls, tuple(iterable))

    def __hash__(self):
        return tuple.__hash__(self)


class OrdinalBallot(dict, Ballot):
    def __init__(
        self,
        iterable: Iterable[Project] = (),
        name: str | None = None,
        meta: dict | None = None,
    ) -> None:
        if name is None:
            if hasattr(iterable, "name"):
                name = iterable.name
            else:
                name = ""
        if meta is None:
            if hasattr(iterable, "meta"):
                meta = iterable.meta
            else:
                meta = dict()
        dict.__init__(self, {e: None for e in iterable})
        Ballot.__init__(self, name=name, meta=meta)

    def append(self, element):
        self[element] = None

    def __add__(self, other):
        if not isinstance(other, OrdinalBallot):
            raise TypeError("Only ordinal ballots can be added to ordinal ballots")
        result = OrdinalBallot(self, name=self.name, meta=self.meta)
        for e in other:
            result[e] = None
        return result

    def __reversed__(self):
        rev_generator = dict.__reversed__(self)
        res = OrdinalBallot(name=self.name, meta=self.meta)
        for key in rev_generator:
            res.append(key)
        return res

    def index(self, element):
        i = 0
        for e in self:
            if e == element:
                return i
            i += 1
        raise ValueError("{} is not in the ballot".format(element))

    def frozen(self) -> FrozenOrdinalBallot:
        return FrozenOrdinalBallot(self)

    def __eq__(self, other):
        if not isinstance(other, OrdinalBallot):
            return False
        if len(self) != len(other):
            return False
        for e1, e2 in zip(self, other):
            if e1 != e2:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        if not isinstance(other, OrdinalBallot):
            raise TypeError("'<' can only be used between two ordinal ballots")
        for e1, e2 in zip(self, other):
            if e1 < e2:
                return True
            elif e2 > e1:
                return False
        return len(self) < len(other)

    def __le__(self, other):
        if not isinstance(other, OrdinalBallot):
            raise TypeError("'<' can only be used between two ordinal ballots")
        for e1, e2 in zip(self, other):
            if e1 < e2:
                return True
            elif e2 > e1:
                return False
        return len(self) == len(other)

    def __repr__(self):
        return list(self.keys()).__repr__()

    def __str__(self):
        return list(self.keys()).__str__()

    # This allows dict method returning copies of a dict to work
    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(result, name=self.name, meta=self.meta)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


OrdinalBallot._wrap_methods(["copy", "__ior__", "__or__", "__ror__"])
