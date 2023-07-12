from collections.abc import Iterable
from numbers import Number

from pabutools.election.ballot import (
    Ballot,
    CumulativeBallot,
    FrozenBallot,
    FrozenCumulativeBallot,
)
from pabutools.election.profile.cardinalprofile import (
    CardinalProfile,
    CardinalMultiProfile,
)
from pabutools.election.instance import Instance


class CumulativeProfile(CardinalProfile):
    """
    A profile of cardinal ballots. Inherits from `pabutools.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(
        self,
        iterable: Iterable[CumulativeBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = True,
        ballot_type: type[Ballot] = CumulativeBallot,
        legal_min_length: int | None = None,
        legal_max_length: int | None = None,
        legal_min_score: Number | None = None,
        legal_max_score: Number | None = None,
        legal_min_total_score: Number | None = None,
        legal_max_total_score: Number | None = None,
    ) -> None:
        super(CumulativeProfile, self).__init__(
            iterable=iterable,
            instance=instance,
            ballot_validation=ballot_validation,
            ballot_type=ballot_type,
        )
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score
        self.legal_min_total_score = legal_min_total_score
        self.legal_max_total_score = legal_max_total_score

    def as_multiprofile(self):
        return CumulativeMultiProfile(
            instance=self.instance,
            profile=self,
            ballot_validation=self.ballot_validation,
            ballot_type=FrozenCumulativeBallot,
            legal_min_length=self.legal_min_length,
            legal_max_length=self.legal_max_length,
            legal_min_score=self.legal_min_score,
            legal_max_score=self.legal_max_score,
        )

    def sort(self, *, key=None, reverse=None):
        raise NotImplementedError(
            "Cumulative profiles cannot be sorted as cumulative ballots do not support '<'"
        )

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, list) and not isinstance(result, cls):
                    result = cls(
                        result,
                        instance=self.instance,
                        ballot_validation=self.ballot_validation,
                        ballot_type=self.ballot_type,
                        legal_min_length=self.legal_min_length,
                        legal_max_length=self.legal_max_length,
                        legal_min_score=self.legal_min_score,
                        legal_max_score=self.legal_max_score,
                        legal_min_total_score=self.legal_min_total_score,
                        legal_max_total_score=self.legal_max_total_score,
                    )
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


CumulativeProfile._wrap_methods(
    [
        "__add__",
        "__iadd__",
        "__imul__",
        "__mul__",
        "__reversed__",
        "__rmul__",
        "copy",
        "reverse",
    ]
)


class CumulativeMultiProfile(CardinalMultiProfile):
    """
    A profile of cardinal ballots. Inherits from `pabutools.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(
        self,
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
        legal_max_total_score: Number | None = None,
    ) -> None:
        super(CumulativeMultiProfile, self).__init__(
            iterable=iterable,
            instance=instance,
            ballot_validation=ballot_validation,
            ballot_type=ballot_type,
        )
        if profile is not None:
            self.extend(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score
        self.legal_min_total_score = legal_min_total_score
        self.legal_max_total_score = legal_max_total_score

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(
                        result,
                        instance=self.instance,
                        ballot_validation=self.ballot_validation,
                        ballot_type=self.ballot_type,
                        legal_min_length=self.legal_min_length,
                        legal_max_length=self.legal_max_length,
                        legal_min_score=self.legal_min_score,
                        legal_max_score=self.legal_max_score,
                        legal_min_total_score=self.legal_min_total_score,
                        legal_max_total_score=self.legal_max_total_score,
                    )
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


CumulativeMultiProfile._wrap_methods(
    ["copy", "__ior__", "__or__", "__ror__", "__reversed__"]
)
