from collections.abc import Iterable
from numbers import Number

from pbvoting.election.ballot import Ballot, CumulativeBallot, FrozenBallot, FrozenCumulativeBallot
from pbvoting.election.profile.cardinalprofile import CardinalProfile, CardinalMultiProfile
from pbvoting.election.instance import Instance


class CumulativeProfile(CardinalProfile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[CumulativeBallot] = (),
                 instance: Instance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[Ballot] = CumulativeBallot,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Number | None = None,
                 legal_max_score: Number | None = None,
                 legal_min_total_score: Number | None = None,
                 legal_max_total_score: Number | None = None
                 ) -> None:
        super(CumulativeProfile, self).__init__(iterable=iterable, instance=instance,
                                                ballot_validation=ballot_validation, ballot_type=ballot_type)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score
        self.legal_min_total_score = legal_min_total_score
        self.legal_max_total_score = legal_max_total_score

    def as_multiprofile(self):
        return CumulativeMultiProfile(instance=self.instance,
                                      profile=self,
                                      ballot_validation=self.ballot_validation,
                                      ballot_type=FrozenCumulativeBallot,
                                      legal_min_length=self.legal_min_length,
                                      legal_max_length=self.legal_max_length,
                                      legal_min_score=self.legal_min_score,
                                      legal_max_score=self.legal_max_score)

    def __add__(self, value):
        return CumulativeProfile(list.__add__(self, value), instance=self.instance,
                                 ballot_validation=self.ballot_validation,
                                 ballot_type=self.ballot_type,
                                 legal_min_length=self.legal_min_length,
                                 legal_max_length=self.legal_max_length,
                                 legal_min_score=self.legal_min_score,
                                 legal_max_score=self.legal_max_score,
                                 legal_min_total_score=self.legal_min_total_score,
                                 legal_max_total_score=self.legal_max_total_score)

    def __mul__(self, value):
        return CumulativeProfile(list.__mul__(self, value), instance=self.instance,
                                 ballot_validation=self.ballot_validation,
                                 ballot_type=self.ballot_type,
                                 legal_min_length=self.legal_min_length,
                                 legal_max_length=self.legal_max_length,
                                 legal_min_score=self.legal_min_score,
                                 legal_max_score=self.legal_max_score,
                                 legal_min_total_score=self.legal_min_total_score,
                                 legal_max_total_score=self.legal_max_total_score)


class CumulativeMultiProfile(CardinalMultiProfile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[FrozenCumulativeBallot] = (),
                 instance: Instance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenCumulativeBallot,
                 profile: CumulativeProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Number | None = None,
                 legal_max_score: Number | None = None,
                 legal_min_total_score: Number | None = None,
                 legal_max_total_score: Number | None = None
                 ) -> None:
        super(CumulativeMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                     ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.extend(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score
        self.legal_min_total_score = legal_min_total_score
        self.legal_max_total_score = legal_max_total_score

