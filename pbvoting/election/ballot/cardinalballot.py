from pbvoting.election.ballot.ballot import FrozenBallot, Ballot
from pbvoting.election.instance import Project

from numbers import Number


class FrozenCardinalBallot(dict[Project, Number], FrozenBallot):

    def __init__(self,
                 d: dict[Project, Number] = (),
                 name: str | None = None,
                 meta: dict | None = None):
        dict.__init__(self, d)
        if name is None:
            if hasattr(d, "name"):
                name = d.name
            else:
                name = ""
        if meta is None:
            if hasattr(d, "meta"):
                name = d.meta
            else:
                name = ""
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))


class CardinalBallot(dict[Project, Number], Ballot):
    """
        A cardinal ballot, that is, a ballot in which the voter has indicated a score for every project. It is a
        subclass of `Ballot`.
        Attributes
        ----------
            d : dict of projects: score
                The score assigned to the projects. The keys are the projects and map to the score.
                Defaults to the empty dictionary.
    """

    def __init__(self,
                 d: dict[Project, Number] = None,
                 name: str | None = None,
                 meta: dict | None = None):
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
        Ballot.__init__(self, name=name, meta=meta)

    def complete(self, projects, default_score):
        for project in projects:
            if project not in self:
                self[project] = default_score

    def freeze(self):
        return FrozenCardinalBallot(self)

    # This allows dict method returning copies of a dict to work
    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(result,
                                 name=self.name,
                                 meta=self.meta)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


CardinalBallot._wrap_methods(['fromkeys', 'copy', '__ior__', '__or__', '__ror__'])
