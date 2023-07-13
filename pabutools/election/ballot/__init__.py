"""
Module describing different ballot formats that can be used. A ballot is the entity that contains the information
submitted by a voter in an election. It can take many forms, from simple approval ballots in which a voter just
indicates the projects they approve of, to more complex cardinal ballot in which a score is assigned to the projects.
"""

from pabutools.election.ballot.ballot import Ballot, FrozenBallot, AbstractBallot
from pabutools.election.ballot.approvalballot import (
    ApprovalBallot,
    FrozenApprovalBallot,
    get_random_approval_ballot,
)
from pabutools.election.ballot.cardinalballot import (
    CardinalBallot,
    FrozenCardinalBallot,
)
from pabutools.election.ballot.cumulativeballot import (
    CumulativeBallot,
    FrozenCumulativeBallot,
)
from pabutools.election.ballot.ordinalballot import OrdinalBallot, FrozenOrdinalBallot

__all__ = [
    "Ballot",
    "FrozenBallot",
    "AbstractBallot",
    "ApprovalBallot",
    "FrozenApprovalBallot",
    "get_random_approval_ballot",
    "CardinalBallot",
    "FrozenCardinalBallot",
    "CumulativeBallot",
    "FrozenCumulativeBallot",
    "OrdinalBallot",
    "FrozenOrdinalBallot"
]
