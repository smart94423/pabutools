from pbvoting.election.ballot.ballot import FrozenBallot
from pbvoting.election.ballot.cardinalballot import CardinalBallot
from pbvoting.election.instance import Project

from numbers import Number


class FrozenCumulativeBallot(dict[Project, Number], FrozenBallot):
    def __init__(
        self,
        d: dict[Project, Number] = None,
        name: str | None = None,
        meta: dict | None = None,
    ):
        if d is None:
            d = dict()
        dict.__init__(self, d)
        if name is None:
            if hasattr(d, "name"):
                name = d.name
            else:
                name = ""
        if meta is None:
            if hasattr(d, "meta"):
                meta = d.meta
            else:
                meta = dict
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))


class CumulativeBallot(CardinalBallot):
    """
    A cumulative ballot, that is, a ballot in which the voter has indicated a score for every project using a
    total number of points allocated to the voter. It is a subclass of `pbvoting.instance.profile.Ballot`.
    Attributes
    """

    def __init__(
        self,
        d: dict[Project, Number] = None,
        name: str | None = None,
        meta: dict | None = None,
    ):
        if d is None:
            d = dict()
        if name is None:
            if hasattr(d, "name"):
                name = d.name
            else:
                name = ""
        if meta is None:
            if hasattr(d, "meta"):
                meta = d.meta
            else:
                meta = dict
        CardinalBallot.__init__(self, d, name=name, meta=meta)

    def frozen(self):
        return FrozenCumulativeBallot(self)

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


CumulativeBallot._wrap_methods(["copy", "__ior__", "__or__", "__ror__", "__reversed__"])
