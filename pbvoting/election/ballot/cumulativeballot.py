from pbvoting.election.ballot.ballot import FrozenBallot
from pbvoting.election.ballot.cardinalballot import CardinalBallot
from pbvoting.election.instance import Project

from numbers import Number


class CumulativeBallot(CardinalBallot):
    """
        A cumulative ballot, that is, a ballot in which the voter has indicated a score for every project using a
        total number of points allocated to the voter. It is a subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
    """

    def __init__(self,
                 d: dict[Project, Number] = None,
                 name: str = "",
                 meta: dict | None = None):
        if d is None:
            d = {}
        dict.__init__(self, d)
        CardinalBallot.__init__(self, name=name, meta=meta)


class FrozenCumulativeBallot(dict[Project, Number], FrozenBallot):

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
