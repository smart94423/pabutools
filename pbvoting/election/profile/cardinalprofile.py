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

    def sort(self, *, key=None, reverse=None):
        raise NotImplementedError("Cardinal profiles cannot be sorted as cardinal ballots do not support '<'")

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, list) and not isinstance(result, cls):
                    result = cls(result,
                                 instance=self.instance,
                                 ballot_validation=self.ballot_validation,
                                 ballot_type=self.ballot_type,
                                 legal_min_length=self.legal_min_length,
                                 legal_max_length=self.legal_max_length,
                                 legal_min_score=self.legal_min_score,
                                 legal_max_score=self.legal_max_score)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


CardinalProfile._wrap_methods(['__add__', '__iadd__', '__imul__', '__mul__', '__reversed__', '__rmul__', 'copy',
                               'reverse'])


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

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(result,
                                 instance=self.instance,
                                 ballot_validation=self.ballot_validation,
                                 ballot_type=self.ballot_type,
                                 legal_min_length=self.legal_min_length,
                                 legal_max_length=self.legal_max_length,
                                 legal_min_score=self.legal_min_score,
                                 legal_max_score=self.legal_max_score)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


CardinalMultiProfile._wrap_methods(['copy', '__ior__', '__or__', '__ror__', '__reversed__'])
