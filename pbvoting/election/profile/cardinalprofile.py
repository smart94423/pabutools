from collections.abc import Iterable
from numbers import Number

from pbvoting.election.ballot import Ballot, CardinalBallot, FrozenBallot, FrozenCardinalBallot
from pbvoting.election.profile.profile import Profile, MultiProfile
from pbvoting.election.instance import Instance, Project


class CardinalProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[CardinalBallot] = (),
                 instance: Instance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[Ballot] = CardinalBallot,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Number | None = None,
                 legal_max_score: Number | None = None
                 ) -> None:
        super(CardinalProfile, self).__init__(iterable=iterable, instance=instance, ballot_validation=ballot_validation,
                                              ballot_type=ballot_type)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score

    def as_multiprofile(self):
        return CardinalMultiProfile(instance=self.instance,
                                    profile=self,
                                    ballot_validation=self.ballot_validation,
                                    ballot_type=FrozenCardinalBallot,
                                    legal_min_length=self.legal_min_length,
                                    legal_max_length=self.legal_max_length,
                                    legal_min_score=self.legal_min_score,
                                    legal_max_score=self.legal_max_score)

    def __add__(self, value):
        return CardinalProfile(list.__add__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
                               ballot_type=self.ballot_type,
                               legal_min_length=self.legal_min_length,
                               legal_max_length=self.legal_max_length,
                               legal_min_score=self.legal_min_score,
                               legal_max_score=self.legal_max_score)

    def __mul__(self, value):
        return CardinalProfile(list.__mul__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
                               ballot_type=self.ballot_type,
                               legal_min_length=self.legal_min_length,
                               legal_max_length=self.legal_max_length,
                               legal_min_score=self.legal_min_score,
                               legal_max_score=self.legal_max_score)

    def score(self, project: Project) -> Number:
        """
            Returns the score of a project, that is, the sum of scores received from all voters.
            Parameters
            ----------
                project : pbvoting.instance.instance.Project
                    The project.
            Returns
            -------
                Fraction
        """
        score = 0
        for ballot in self:
            if project in ballot:
                score += ballot[project]
        return score

    def complete(self, projects, default_score):
        for ballot in self:
            ballot.complete(projects, default_score)


class CardinalMultiProfile(MultiProfile):
    """
    """

    def __init__(self,
                 iterable: Iterable[FrozenCardinalBallot] = (),
                 instance: Instance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenCardinalBallot,
                 profile: CardinalProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Number | None = None,
                 legal_max_score: Number | None = None
                 ) -> None:
        super(CardinalMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                   ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.extend(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score

