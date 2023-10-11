"""
Profiles, i.e., collections of ballots.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from abc import ABC, abstractmethod

from pabutools.election.satisfaction import (
    SatisfactionMeasure,
    SatisfactionProfile,
    SatisfactionMultiProfile,
    GroupSatisfactionMeasure,
)
from pabutools.election.ballot import AbstractBallot, FrozenBallot, Ballot
from pabutools.election.instance import Instance


class AbstractProfile(ABC, Iterable[AbstractBallot]):
    """
    Abstract class representing a profile, that is, a collection of ballots. This class is only meant to be inherited.

    Parameters
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`, optional
            The instance related to the profile.
            Defaults to `Instance()`.
        ballot_validation : bool, optional
            Boolean indicating whether ballots should be validated before being added to the profile.
            Defaults to `True`.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`], optional
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
            Defaults to `AbstractBallot`.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance related to the profile.
        ballot_validation : bool
            Boolean indicating whether ballots should be validated before being added to the profile.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`]
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.

    """

    def __init__(
        self,
        instance: Instance | None = None,
        ballot_validation: bool = None,
        ballot_type: type[AbstractBallot] = None,
    ) -> None:
        ABC.__init__(self)
        Iterable.__init__(self)
        if instance is None:
            instance = Instance()
        self.instance = instance
        self.ballot_validation = ballot_validation
        if ballot_type is None:
            ballot_type = AbstractBallot
        self.ballot_type = ballot_type

    def validate_ballot(self, ballot: AbstractBallot) -> None:
        """
        Method validating a ballot before adding it to the profile. Checks if the type of the ballot is a subclass of
        the attribute `ballot_type`. Throws a `TypeError` if not, and returns `None` otherwise.

        Parameters
        ----------
            ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
                The ballot to be checked.
        """
        if self.ballot_validation and not isinstance(ballot, self.ballot_type):
            raise TypeError(
                "Ballot type {} is invalid, the profile expected a subclass of {}.".format(
                    type(ballot), self.ballot_type
                )
            )

    @abstractmethod
    def multiplicity(self, ballot: AbstractBallot) -> int:
        """
        Method returning the multiplicity of a ballot. Used to ensure that
        :py:class:`~pabutools.election.profile.profile.Profile` and
        :py:class:`~pabutools.election.profile.profile.MultiProfile` can be used interchangeably.

        Parameters
        ----------
            ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                The multiplicity of the ballots.
        """

    @abstractmethod
    def as_sat_profile(
        self, sat_class: type[SatisfactionMeasure]
    ) -> GroupSatisfactionMeasure:
        """
        Converts the profile into a satisfaction profile. See the :py:mod:`~pabutools.election.satisfaction` for more
        details.

        Parameters
        ----------
            sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
                The class for the representing the satisfaction measure to use.

        Returns
        -------
            py:class:`~pabutools.election.satisfaction.satisfactionmeasure.GroupSatisfactionMeasure`
                A satisfaction profile, that is, a collection of satisfaction measures for all the voters.
        """

    @abstractmethod
    def num_ballots(self) -> int:
        """
        Returns the number of ballots appearing in the profile. Used to ensure that
        :py:class:`~pabutools.election.profile.profile.Profile` and
        :py:class:`~pabutools.election.profile.profile.MultiProfile` can be used interchangeably.

        Returns
        -------
            int
                The number of voters.

        """


class Profile(list, AbstractProfile):
    """
    A profile, that is, a list of ballots per voters. This class inherits from the Python `list` class and can thus
    be used as one. All other profile classes inherit form this one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.ballot.ballot.Ballot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.ballot.Ballot` that is used as initializer for the
            list. If activated, the types of the ballots are validated. In case an
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
            Defaults to `Ballot`.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance related to the profile.
        ballot_validation : bool
            Boolean indicating whether ballots should be validated before being added to the profile.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`]
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
    """

    def __init__(
        self,
        init: Iterable[Ballot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = None,
        ballot_type: type[Ballot] = None,
    ) -> None:
        if ballot_validation is None:
            if isinstance(init, AbstractProfile):
                ballot_validation = init.ballot_validation
            else:
                ballot_validation = True
        if ballot_type is None:
            if isinstance(init, AbstractProfile):
                ballot_type = init.ballot_type
            else:
                ballot_type = Ballot
        if instance is None:
            if isinstance(init, AbstractProfile):
                instance = init.instance
            else:
                instance = Instance()
        AbstractProfile.__init__(self, instance, ballot_validation, ballot_type)
        init = list(init)  # in case `init` is an iterable
        if ballot_validation:
            for item in init:
                self.validate_ballot(item)
        super().__init__(init)

    def multiplicity(self, ballot: Ballot) -> int:
        """
        Returns 1 regardless of the input (even if the ballot does not appear in the profile, to save up computation).

        Parameters
        ----------
            ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
                The ballot whose multiplicity is inquired.

        Returns
        -------
            int
                1
        """
        return 1

    @abstractmethod
    def as_multiprofile(self) -> MultiProfile:
        """
        Converts the profile into a :py:class:`~pabutools.election.profile.profile.MultiProfile`.

        Returns
        -------
            :py:class:`~pabutools.election.profile.profile.MultiProfile`
                The multiprofile corresponding to the profile.
        """

    def as_sat_profile(self, sat_class: type[SatisfactionMeasure]):
        return SatisfactionProfile(
            instance=self.instance, profile=self, sat_class=sat_class
        )

    def num_ballots(self) -> int:
        return len(self)

    def __add__(self, value):
        return Profile(
            list.__add__(self, value),
            instance=self.instance,
            ballot_validation=self.ballot_validation,
        )

    def __mul__(self, value):
        return Profile(
            list.__mul__(self, value),
            instance=self.instance,
            ballot_validation=self.ballot_validation,
        )

    def __setitem__(self, index, item):
        self.validate_ballot(item)
        list.__setitem__(self, index, item)

    def insert(self, index: int, item: Ballot) -> None:
        self.validate_ballot(item)
        list.insert(self, index, item)

    def append(self, item: Ballot) -> None:
        self.validate_ballot(item)
        list.append(self, item)

    def extend(self, other) -> None:
        for item in other:
            self.validate_ballot(item)
        list.extend(self, other)


class MultiProfile(Counter, AbstractProfile):
    """
    A multiprofile, that is, a profile that stores the ballots together with their multiplicity. This class inherits
    from the Python `Counter` class (a special type of `dict` meant to represent multisets) and can be used as one.
    All other multiprofile classes inherit form this one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.ballot.ballot.Ballot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.ballot.Ballot` that is used as initializer for the
            list. If activated, the types of the ballots are validated. In case an
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
            Defaults to `FrozenBallot`.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance related to the profile.
        ballot_validation : bool
            Boolean indicating whether ballots should be validated before being added to the profile.
        ballot_type : type[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`]
            The type that the ballots are validated against. If `ballot_validation` is `True` and a ballot of a type
            that is not a subclass of `ballot_type` is added, an exception will be raised.
    """

    def __init__(
        self,
        init: Iterable[FrozenBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = None,
        ballot_type: type[FrozenBallot] = None,
    ) -> None:
        if ballot_validation is None:
            if isinstance(init, AbstractProfile):
                ballot_validation = init.ballot_validation
            else:
                ballot_validation = True
        if ballot_type is None:
            if isinstance(init, AbstractProfile):
                ballot_type = init.ballot_type
            else:
                ballot_type = FrozenBallot
        if instance is None:
            if isinstance(init, AbstractProfile):
                instance = init.instance
            else:
                instance = Instance()
        AbstractProfile.__init__(self, instance, ballot_validation, ballot_type)
        if ballot_validation:
            for item in init:
                self.validate_ballot(item)
        Counter.__init__(self, init)

    def multiplicity(self, ballot: FrozenBallot) -> int:
        return self[ballot]

    def as_sat_profile(self, sat_class: type[SatisfactionMeasure]):
        return SatisfactionMultiProfile(
            instance=self.instance, multiprofile=self, sat_class=sat_class
        )

    def num_ballots(self) -> int:
        return self.total()

    def __setitem__(self, key, value):
        self.validate_ballot(key)
        Counter.__setitem__(self, key, value)

    def append(self, ballot: AbstractBallot):
        """
        Appends a ballot to the profile and update the multiplicity if necessary.

        Parameters
        ----------
            ballot : :py:class:`~pabutools.election.ballot.ballot.AbstractBallot`
                The ballot to append to the profile.

        """
        self.validate_ballot(ballot)
        if ballot in self:
            self[ballot] += 1
        else:
            self[ballot] = 1

    def extend(self, iterable: Iterable[AbstractBallot], force_freeze=True):
        """
        Extends the profile by appending all the ballots in the iterable.

        Parameters
        ----------
            iterable : Iterable[:py:class:`~pabutools.election.ballot.ballot.AbstractBallot`]
                An iterable of ballots to add to the profile.
            force_freeze : bool, optional
                Boolean indicating whether subclasses of :py:class:`~pabutools.election.ballot.ballot.Ballot` should be
                frozen beforehand.
                Defaults to `True`.

        """
        for ballot in iterable:
            if isinstance(ballot, Ballot) and force_freeze:
                self.append(ballot.frozen())
            else:
                self.append(ballot)
