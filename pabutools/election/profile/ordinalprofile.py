from __future__ import annotations

from abc import ABC
from collections.abc import Iterable

from pabutools.election.ballot import (
    Ballot,
    OrdinalBallot,
    FrozenBallot,
    FrozenOrdinalBallot,
)
from pabutools.election.profile.profile import Profile, MultiProfile, AbstractProfile
from pabutools.election.instance import Instance


class AbstractOrdinalProfile(AbstractProfile, ABC):
    """
    Abstract class for ordinal profiles. Stores the metadata and the methods specific to ordinal profiles.

    Parameters
    ----------
        legal_min_length : int, optional
            The minimum length of an ordinal ballot per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum length of an ordinal ballot per the rules of the election.
            Defaults to `None`.

    Attributes
    ----------
        legal_min_length : int
            The minimum length of an ordinal ballot per the rules of the election.
        legal_max_length : int
            The maximum length of an ordinal ballot per the rules of the election.
    """

    def __init__(
        self,
        legal_min_length: int | None = None,
        legal_max_length: int | None = None,
    ):
        AbstractProfile.__init__(self)
        ABC.__init__(self)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length


class OrdinalProfile(Profile, AbstractOrdinalProfile):
    """
    A profile of ordinal ballots, that is, a list of ordinal ballots per voters. See the class
    :py:class:`~pabutools.election.ballot.ordinalballot.OrdinalBallot` for more details on ordinal ballots.
    This class inherits from the Python `list` class and can thus be used as one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.ballot.ordinalballot.OrdinalBallot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.ordinalballot.OrdinalBallot` that is used an
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
            Defaults to `OrdinalBallot`.
        legal_min_length : int, optional
            The minimum length of an ordinal ballot per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum length of an ordinal ballot per the rules of the election.
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
            The minimum length of an ordinal ballot per the rules of the election.
        legal_max_length : int
            The maximum length of an ordinal ballot per the rules of the election.
    """

    def __init__(
        self,
        init: Iterable[OrdinalBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool | None = None,
        ballot_type: type[Ballot] | None = None,
        legal_min_length: int | None = None,
        legal_max_length: int | None = None,
    ) -> None:
        if legal_min_length is None and isinstance(init, AbstractOrdinalProfile):
            legal_min_length = init.legal_min_length
        if legal_max_length is None and isinstance(init, AbstractOrdinalProfile):
            legal_max_length = init.legal_max_length
        AbstractOrdinalProfile.__init__(
            self,
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
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
                ballot_type = OrdinalBallot
        if instance is None and isinstance(init, AbstractOrdinalProfile):
            instance = init.instance
        Profile.__init__(
            self,
            init=init,
            instance=instance,
            ballot_validation=ballot_validation,
            ballot_type=ballot_type,
        )

    def as_multiprofile(self):
        """
        Converts the profile into a :py:class:`~pabutools.election.profile.ordinalprofile.OrdinalMultiProfile`.

        Returns
        -------
            :py:class:`~pabutools.election.profile.ordinalprofile.OrdinalMultiProfile`
                The multiprofile corresponding to the profile.
        """
        return OrdinalMultiProfile(
            instance=self.instance,
            profile=self,
            ballot_validation=self.ballot_validation,
            ballot_type=FrozenOrdinalBallot,
            legal_min_length=self.legal_min_length,
            legal_max_length=self.legal_max_length,
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
                    )
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


OrdinalProfile._wrap_methods(
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


class OrdinalMultiProfile(MultiProfile, AbstractOrdinalProfile):
    """
    A multiprofile of ordinal ballots, that is, a multiset of ordinal ballots together with their multiplicity.
    Ballots needs to be hashable, so the class
    :py:class:`~pabutools.election.ballot.ordinalballot.FrozenOrdinalBallot` should be used by default here.
    This class inherits from the Python `Counter` class and can thus be used as one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.ballot.ordinalballot.FrozenOrdinalBallot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.ordinalballot.FrozenOrdinalBallot` that is used an
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
            Defaults to `ForzenOrdinalBallot`.
        profile: :py:class:`~pabutools.election.profile.ordinalprofile.OrdinalProfile`, optional
            A profile used to initialise the multiprofile. Some metadata are taken from the profile if they are not
            specified in the constructor.
        legal_min_length : int, optional
            The minimum length of an ordinal ballot per the rules of the election.
            Defaults to `None`.
        legal_max_length : int, optional
            The maximum length of an ordinal ballot per the rules of the election.
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
            The minimum length of an ordinal ballot per the rules of the election.
        legal_max_length : int
            The maximum length of an ordinal ballot per the rules of the election.
    """

    def __init__(
        self,
        init: Iterable[FrozenOrdinalBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool | None = None,
        ballot_type: type[FrozenBallot] | None = None,
        profile: OrdinalProfile | None = None,
        legal_min_length: int | None = None,
        legal_max_length: int | None = None,
    ) -> None:
        if legal_min_length is None:
            if isinstance(init, AbstractOrdinalProfile):
                legal_min_length = init.legal_min_length
            elif profile:
                legal_min_length = profile.legal_min_length
        if legal_max_length is None:
            if isinstance(init, AbstractOrdinalProfile):
                legal_max_length = init.legal_max_length
            elif profile:
                legal_max_length = profile.legal_max_length
        AbstractOrdinalProfile.__init__(
            self,
            legal_min_length=legal_min_length,
            legal_max_length=legal_max_length,
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
                ballot_type = FrozenOrdinalBallot
        if instance is None:
            if isinstance(init, AbstractOrdinalProfile):
                instance = init.instance
            elif profile:
                instance = profile.instance
        MultiProfile.__init__(
            self,
            init=init,
            instance=instance,
            ballot_validation=ballot_validation,
            ballot_type=ballot_type,
        )
        if profile is not None:
            self.extend(profile)

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
        )


OrdinalMultiProfile._wrap_methods(
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
