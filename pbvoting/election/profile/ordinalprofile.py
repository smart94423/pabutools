from collections.abc import Iterable

from pbvoting.election.ballot import Ballot, OrdinalBallot, FrozenBallot, FrozenOrdinalBallot
from pbvoting.election.profile.profile import Profile, MultiProfile
from pbvoting.election.instance import Instance


class OrdinalProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[OrdinalBallot] = (),
                 instance: Instance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[Ballot] = OrdinalBallot,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None
                 ) -> None:
        super(OrdinalProfile, self).__init__(iterable=iterable, instance=instance, ballot_validation=ballot_validation,
                                             ballot_type=OrdinalBallot)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length

    def as_multiprofile(self):
        return OrdinalMultiProfile(instance=self.instance,
                                   profile=self,
                                   ballot_validation=self.ballot_validation,
                                   ballot_type=FrozenOrdinalBallot,
                                   legal_min_length=self.legal_min_length,
                                   legal_max_length=self.legal_max_length)

    def __add__(self, value):
        return OrdinalProfile(list.__add__(self, value), instance=self.instance,
                              ballot_validation=self.ballot_validation,
                              ballot_type=self.ballot_type,
                              legal_min_length=self.legal_min_length,
                              legal_max_length=self.legal_max_length)

    def __mul__(self, value):
        return OrdinalProfile(list.__mul__(self, value), instance=self.instance,
                              ballot_validation=self.ballot_validation,
                              ballot_type=self.ballot_type,
                              legal_min_length=self.legal_min_length,
                              legal_max_length=self.legal_max_length)


class OrdinalMultiProfile(MultiProfile):
    """
    """

    def __init__(self,
                 iterable: Iterable[FrozenOrdinalBallot] = (),
                 instance: Instance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenOrdinalBallot,
                 profile: OrdinalProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None
                 ) -> None:
        super(OrdinalMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                  ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.extend(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
