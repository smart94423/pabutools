from pbvoting.election.ballot.ballot import FrozenBallot, Ballot
from pbvoting.election.instance import Project

from numbers import Number


class CardinalBallot(dict[Project, Number], Ballot):
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
                 d: dict[Project, Number] = None,
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


class FrozenCardinalBallot(dict[Project, Number], FrozenBallot):

    def __init__(self,
                 d: dict[Project, Number] = (),
                 name: str = "",
                 meta: dict | None = None):
        dict.__init__(self, d)
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))
