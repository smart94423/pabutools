"""
Preference profiles and voters.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from abc import ABC, abstractmethod

from pabutools.election.satisfaction import (
    SatisfactionMeasure,
    SatisfactionProfile,
    SatisfactionMultiProfile,
    GroupSatisfactionMeasure
)
from pabutools.election.ballot import AbstractBallot, FrozenBallot, Ballot
from pabutools.election.instance import Instance


class AbstractProfile(ABC):
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
        ballot_validation: bool = True,
        ballot_type: type[AbstractBallot] = None,
    ) -> None:
        super().__init__()
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
        if self.ballot_validation and not issubclass(type(ballot), self.ballot_type):
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
        ...

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
        ...

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
        ...


class Profile(list, AbstractProfile):
    """
    A profile, that is, a list of ballots per voters. This class inherits from the Python `list` class and can thus
    be used as one. All other profile classes inherit form this one.

    Parameters
    ----------
        iterable : Iterable[:py:class:`~pabutools.election.ballot.ballot.Ballot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.ballot.Ballot` that is used an initializer for the
            list. If activated, the types of the ballots are validated. In case an
            :py:class:`~pabutools.election.ballot.ballot.AbstractBallot` object is passed, the
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
        iterable: Iterable[Ballot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = True,
        ballot_type: type[Ballot] = None,
    ) -> None:
        if ballot_type is None:
            ballot_type = Ballot
        AbstractProfile.__init__(self, instance, ballot_validation, ballot_type)
        for item in iterable:
            self.validate_ballot(item)
        list.__init__(self, iterable)

    def multiplicity(self, ballot: Ballot) -> int:
        return 1

    def as_multiprofile(self) -> MultiProfile:
        """
        Converts the profile into a :py:class:`~pabutools.election.profile.profile.MultiProfile`.

        Returns
        -------
            :py:class:`~pabutools.election.profile.profile.MultiProfile`
                The multiprofile corresponding to the profile.
        """
        ...

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
        super().__setitem__(index, item)

    def insert(self, index: int, item: Ballot) -> None:
        self.validate_ballot(item)
        super().insert(index, item)

    def append(self, item: Ballot) -> None:
        self.validate_ballot(item)
        super().append(item)

    def extend(self, other) -> None:
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(item for item in other if self.validate_ballot(item) is None)


class MultiProfile(Counter, AbstractProfile):
    """
    A multiprofile, that is, a profile that stores the ballots together with their multiplicity. This class inherits
    from the Python `Counter` class (a special type of `dict` meant to represent multisets) and can be used as one.
    All other multiprofile classes inherit form this one.

    Parameters
    ----------
        iterable : Iterable[:py:class:`~pabutools.election.ballot.ballot.Ballot`], optional
            An iterable of :py:class:`~pabutools.election.ballot.ballot.Ballot` that is used an initializer for the
            list. If activated, the types of the ballots are validated. In case an
            :py:class:`~pabutools.election.ballot.ballot.AbstractBallot` object is passed, the
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
        iterable: Iterable[FrozenBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = True,
        ballot_type: type[FrozenBallot] = None,
    ) -> None:
        if ballot_type is None:
            ballot_type = FrozenBallot
        AbstractProfile.__init__(self, instance, ballot_validation, ballot_type)
        for item in iterable:
            self.validate_ballot(item)
        Counter.__init__(self, iterable)

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
        super().__setitem__(key, value)

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
            if issubclass(type(ballot), Ballot) and force_freeze:
                self.append(ballot.frozen())
            else:
                self.append(ballot)
