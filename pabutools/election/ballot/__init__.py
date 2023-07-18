"""
Module describing different ballot formats that can be used. A ballot is the entity that contains the information
submitted by a voter in an election. It can take many forms, from simple approval ballots in which a voter just
indicates the projects they approve of, to more complex cardinal ballot in which a score is assigned to the projects.

This module introduces the abstract class :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`,
that all ballot classes inherit from. Two general categories of ballots are also introduced. First, the standard
ballots, that all inherit from the class :py:class:`~pabutools.election.ballot.ballot.Ballot`. These ballots correspond
to the following classes:

* :py:class:`~pabutools.election.ballot.approvalballot.ApprovalBallot`
* :py:class:`~pabutools.election.ballot.cardinalballot.CardinalBallot`
* :py:class:`~pabutools.election.ballot.cumulativeballot.CumulativeBallot`
* :py:class:`~pabutools.election.ballot.ordinalballot.OrdinalBallot`

The second category of ballot this module defines are the so-called frozen ballots. These are ballots that behave
exactly as the corresponding regular ballots, but that are not mutable, and thus are hashable. These classes are
important for us as they allow ballots to be key of dictionaries (see the
:py:class:`~pabutools.election.profile.profile.MultiProfile` class). These ballots correspond
to the following classes:

* :py:class:`~pabutools.election.ballot.approvalballot.FrozenApprovalBallot`
* :py:class:`~pabutools.election.ballot.cardinalballot.FrozenCardinalBallot`
* :py:class:`~pabutools.election.ballot.cumulativeballot.FrozenCumulativeBallot`
* :py:class:`~pabutools.election.ballot.ordinalballot.FrozenOrdinalBallot`

For typing purposes, we introduce abstract classes for each type of ballots:

* :py:class:`~pabutools.election.ballot.approvalballot.AbstractApprovalBallot`
* :py:class:`~pabutools.election.ballot.cardinalballot.AbstractCardinalBallot`
* :py:class:`~pabutools.election.ballot.cumulativeballot.AbstractCumulativeBallot`
* :py:class:`~pabutools.election.ballot.ordinalballot.AbstractOrdinalBallot`
"""

from pabutools.election.ballot.ballot import Ballot, FrozenBallot, AbstractBallot
from pabutools.election.ballot.approvalballot import (
    AbstractApprovalBallot,
    ApprovalBallot,
    FrozenApprovalBallot,
    get_random_approval_ballot,
)
from pabutools.election.ballot.cardinalballot import (
    AbstractCardinalBallot,
    CardinalBallot,
    FrozenCardinalBallot,
)
from pabutools.election.ballot.cumulativeballot import (
    AbstractCumulativeBallot,
    CumulativeBallot,
    FrozenCumulativeBallot,
)
from pabutools.election.ballot.ordinalballot import (
    AbstractOrdinalBallot,
    OrdinalBallot,
    FrozenOrdinalBallot,
)

__all__ = [
    "Ballot",
    "FrozenBallot",
    "AbstractBallot",
    "AbstractApprovalBallot",
    "ApprovalBallot",
    "FrozenApprovalBallot",
    "get_random_approval_ballot",
    "AbstractCardinalBallot",
    "CardinalBallot",
    "FrozenCardinalBallot",
    "AbstractCumulativeBallot",
    "CumulativeBallot",
    "FrozenCumulativeBallot",
    "AbstractOrdinalBallot",
    "OrdinalBallot",
    "FrozenOrdinalBallot",
]
