from abc import ABC
from collections.abc import Iterable
from copy import deepcopy
from numbers import Number

from pabutools.election.profile.profile import AbstractProfile

from pabutools.election.ballot import (
    Ballot,
    CumulativeBallot,
    FrozenBallot,
    FrozenCumulativeBallot,
)
from pabutools.election.profile.cardinalprofile import (
    CardinalProfile,
    CardinalMultiProfile,
    AbstractCardinalProfile,
)
from pabutools.election.instance import Instance


class AbstractCumulativeProfile(AbstractCardinalProfile, ABC):
    """
    Abstract class for cumulative profiles. Stores the metadata and the methods specific to cumulative profiles.

    Parameters
    ----------
        legal_min_length : int, optional
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_min_score : Number, optional
            The minimum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_max_score : Number, optional
            The maximum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_min_total_score : Number, optional
            Minimum total score that can be assigned across all projects per the rules of the election.
            Defaults to `None`.
        legal_max_total_score : Number, optional
            Maximum total score that can be assigned across all projects per the rules of the election.
            Defaults to `None`.

    Attributes
    ----------
        legal_min_length : int
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
        legal_max_length : int
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
        legal_min_score : Number
            The minimum score a project can be assigned by a voter per the rules of the election.
        legal_max_score : Number
            The maximum score a project can be assigned by a voter per the rules of the election.
        legal_min_total_score : Number
            Minimum total score that can be assigned across all projects per the rules of the election.
        legal_max_total_score : Number
            Maximum total score that can be assigned across all projects per the rules of the election.
    """

    def __init__(
        self,
        legal_min_length: int | None = None,
        legal_max_length: int | None = None,
        legal_min_score: Number | None = None,
        legal_max_score: Number | None = None,
        legal_min_total_score: Number | None = None,
        legal_max_total_score: Number | None = None,
    ):
        AbstractCardinalProfile.__init__(
            self,
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
            legal_min_score=legal_min_score,
            legal_max_score=legal_max_score,
        )
        ABC.__init__(self)
        self.legal_min_total_score = legal_min_total_score
        self.legal_max_total_score = legal_max_total_score


class CumulativeProfile(CardinalProfile, AbstractCumulativeProfile):
    """
    A profile of cumulative ballots, that is, a list of cumulative ballots per voters. See the class
    :py:class:`~pabutools.election.ballot.cumulativeballot.CumulativeBallot` for more details on cumulative ballots.
    This class inherits from the Python `list` class and can thus be used as one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.ballot.cumulativeballot.CumulativeBallot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.cumulativeballot.CumulativeBallot` that is used an
            initializer for the list. If activated, the types of the ballots are validated. In case an
            :py:class:`~pabutools.election.profile.profile.AbstractProfile` object is passed, the
            additional attributes are also copied (except if the corresponding keyword arguments have been given).
        instance : :py:class:`~pabutools.election.instance.Instance`, optional
            The instance related to the profile.
            Defaults to `Instance()`.
        ballot_validation : bool, optional
            Boolean indicating whether ballots should be validated before being added to the profile.
            Defaults to `True`.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`], optional
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
            Defaults to `CumulativeBallot`.
        legal_min_length : int, optional
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_min_score : Number, optional
            The minimum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_max_score : Number, optional
            The maximum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_min_total_score : Number, optional
            Minimum total score that can be assigned across all projects per the rules of the election.
            Defaults to `None`.
        legal_max_total_score : Number, optional
            Maximum total score that can be assigned across all projects per the rules of the election.
            Defaults to `None`.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance related to the profile.
        ballot_validation : bool
            Boolean indicating whether ballots should be validated before being added to the profile.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`]
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
        legal_min_length : int
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
        legal_max_length : int
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
        legal_min_score : Number
            The minimum score a project can be assigned by a voter per the rules of the election.
        legal_max_score : Number
            The maximum score a project can be assigned by a voter per the rules of the election.
        legal_min_total_score : Number
            Minimum total score that can be assigned across all projects per the rules of the election.
        legal_max_total_score : Number
            Maximum total score that can be assigned across all projects per the rules of the election.
    """

    def __init__(
        self,
        init: Iterable[CumulativeBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = None,
        ballot_type: type[Ballot] = None,
        legal_min_length: int | None = None,
        legal_max_length: int | None = None,
        legal_min_score: Number | None = None,
        legal_max_score: Number | None = None,
        legal_min_total_score: Number | None = None,
        legal_max_total_score: Number | None = None,
    ) -> None:
        if legal_min_length is None and isinstance(init, AbstractCardinalProfile):
            legal_min_length = init.legal_min_length
        if legal_max_length is None and isinstance(init, AbstractCardinalProfile):
            legal_max_length = init.legal_max_length
        if legal_min_score is None and isinstance(init, AbstractCardinalProfile):
            legal_min_score = init.legal_min_score
        if legal_max_score is None and isinstance(init, AbstractCardinalProfile):
            legal_max_score = init.legal_max_score
        if legal_min_total_score is None and isinstance(
            init, AbstractCumulativeProfile
        ):
            legal_min_total_score = init.legal_min_total_score
        if legal_max_total_score is None and isinstance(
            init, AbstractCumulativeProfile
        ):
            legal_max_total_score = init.legal_max_total_score
        AbstractCumulativeProfile.__init__(
            self,
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
            legal_min_score=legal_min_score,
            legal_max_score=legal_max_score,
            legal_min_total_score=legal_min_total_score,
            legal_max_total_score=legal_max_total_score,
        )
        if ballot_validation is None:
            if isinstance(init, AbstractProfile):
                ballot_validation = init.ballot_validation
            else:
                ballot_validation = True
        if ballot_type is None:
            if isinstance(init, AbstractProfile):
                ballot_type = init.ballot_type
            else:
                ballot_type = CumulativeBallot
        if instance is None and isinstance(init, AbstractCardinalProfile):
            instance = init.instance
        CardinalProfile.__init__(
            self,
            init=init,
            instance=instance,
            ballot_validation=ballot_validation,
            ballot_type=ballot_type,
        )

    def as_multiprofile(self):
        """
        Converts the profile into a :py:class:`~pabutools.election.profile.cumulativeprofile.CumulativeMultiProfile`.

        Returns
        -------
            :py:class:`~pabutools.election.profile.cumulativeprofile.CumulativeMultiProfile`
                The multiprofile corresponding to the profile.
        """
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
        "__getitem__",
    ]
)


class CumulativeMultiProfile(CardinalMultiProfile, AbstractCumulativeProfile):
    """
    A multiprofile of cardinal ballots, that is, a multiset of cumulative ballots together with their multiplicity.
    Ballots needs to be hashable, so the class
    :py:class:`~pabutools.election.ballot.cumulativeballot.FrozenCumulativeBallot` should be used by default here.
    This class inherits from the Python `Counter` class and can thus be used as one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.ballot.cumulativeballot.FrozenCumulativeBallot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.cumulativeballot.FrozenCumulativeBallot` that is used
            as initializer for the list. If activated, the types of the ballots are validated. In case an
            :py:class:`~pabutools.election.profile.profile.AbstractProfile` object is passed, the
            additional attributes are also copied (except if the corresponding keyword arguments have been given).
        instance : :py:class:`~pabutools.election.instance.Instance`, optional
            The instance related to the profile.
            Defaults to `Instance()`.
        ballot_validation : bool, optional
            Boolean indicating whether ballots should be validated before being added to the profile.
            Defaults to `True`.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`], optional
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
            Defaults to `FrozenCumulativeBallot`.
        profile: :py:class:`~pabutools.election.profile.cumulativeprofile.CumulativeProfile`, optional
            A profile used to initialise the multiprofile. Some metadata are taken from the profile if they are not
            specified in the constructor.
        legal_min_length : int, optional
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
            Defaults to `None`.
        legal_min_score : Number, optional
            The minimum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_max_score : Number, optional
            The maximum score a project can be assigned by a voter per the rules of the election.
            Defaults to `None`.
        legal_min_total_score : Number, optional
            Minimum total score that can be assigned across all projects per the rules of the election.
            Defaults to `None`.
        legal_max_total_score : Number, optional
            Maximum total score that can be assigned across all projects per the rules of the election.
            Defaults to `None`.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance related to the profile.
        ballot_validation : bool
            Boolean indicating whether ballots should be validated before being added to the profile.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`]
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
        legal_min_length : int
            The minimum number of projects a voter needs to assign a score to per the rules of the election.
        legal_max_length : int
            The maximum number of projects a voter needs to assign a score to per the rules of the election.
        legal_min_score : Number
            The minimum score a project can be assigned by a voter per the rules of the election.
        legal_max_score : Number
            The maximum score a project can be assigned by a voter per the rules of the election.
        legal_min_total_score : Number
            Minimum total score that can be assigned across all projects per the rules of the election.
        legal_max_total_score : Number
            Maximum total score that can be assigned across all projects per the rules of the election.
    """

    def __init__(
        self,
        init: Iterable[FrozenCumulativeBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = None,
        ballot_type: type[FrozenBallot] = None,
        profile: CumulativeProfile = None,
        legal_min_length: int | None = None,
        legal_max_length: int | None = None,
        legal_min_score: Number | None = None,
        legal_max_score: Number | None = None,
        legal_min_total_score: Number | None = None,
        legal_max_total_score: Number | None = None,
    ) -> None:
        if legal_min_length is None:
            if isinstance(init, AbstractCardinalProfile):
                legal_min_length = init.legal_min_length
            elif profile:
                legal_min_length = profile.legal_min_length
        if legal_max_length is None:
            if isinstance(init, AbstractCardinalProfile):
                legal_max_length = init.legal_max_length
            elif profile:
                legal_max_length = profile.legal_max_length
        if legal_min_score is None:
            if isinstance(init, AbstractCardinalProfile):
                legal_min_score = init.legal_min_score
            elif profile:
                legal_min_score = profile.legal_min_score
        if legal_max_score is None:
            if isinstance(init, AbstractCardinalProfile):
                legal_max_score = init.legal_max_score
            elif profile:
                legal_max_score = profile.legal_max_score
        if legal_min_total_score is None:
            if isinstance(init, AbstractCumulativeProfile):
                legal_min_total_score = init.legal_min_total_score
            elif profile:
                legal_min_total_score = profile.legal_min_total_score
        if legal_max_total_score is None:
            if isinstance(init, AbstractCumulativeProfile):
                legal_max_total_score = init.legal_max_total_score
            elif profile:
                legal_max_total_score = profile.legal_max_total_score
        AbstractCumulativeProfile.__init__(
            self,
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
            legal_min_score=legal_min_score,
            legal_max_score=legal_max_score,
            legal_min_total_score=legal_min_total_score,
            legal_max_total_score=legal_max_total_score,
        )
        if ballot_validation is None:
            if isinstance(init, AbstractProfile):
                ballot_validation = init.ballot_validation
            else:
                ballot_validation = True
        if ballot_type is None:
            if isinstance(init, AbstractProfile):
                ballot_type = init.ballot_type
            else:
                ballot_type = FrozenCumulativeBallot
        if instance is None:
            if isinstance(init, AbstractCardinalProfile):
                instance = init.instance
            elif profile:
                instance = profile.instance
        CardinalMultiProfile.__init__(
            self,
            init=init,
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

    def __reduce__(self):
        return self.__class__, (
            dict(self),
            self.instance,
            self.ballot_validation,
            self.ballot_type,
            None,
            self.legal_min_length,
            self.legal_max_length,
            self.legal_min_score,
            self.legal_max_score,
            self.legal_min_total_score,
            self.legal_max_total_score,
        )


CumulativeMultiProfile._wrap_methods(
    [
        "__add__",
        "__and__",
        "__iadd__",
        "__iand__",
        "__ior__",
        "__isub__",
        "__imul__",
        "__mul__",
        "__or__",
        "__ror__",
        "__sub__",
        "copy",
    ]
)
