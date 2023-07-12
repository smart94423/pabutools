"""
Preference profiles and voters.
"""

from collections import Counter
from collections.abc import Iterable
from abc import ABC, abstractmethod

from pabutools.election.satisfaction import (
    SatisfactionMeasure,
    SatisfactionProfile,
    SatisfactionMultiProfile,
)
from pabutools.election.ballot import AbstractBallot, FrozenBallot, Ballot
from pabutools.election.instance import Instance


class AbstractProfile(ABC):
    """
    Abstract class representing a profile, that is, a collection of ballots.
    """

    def __init__(self):
        super().__init__()

    @abstractmethod
    def validate_ballot(self, ballot: AbstractBallot) -> None:
        ...

    @abstractmethod
    def multiplicity(self, ballot: AbstractBallot) -> int:
        ...

    @abstractmethod
    def as_sat_profile(
        self, sat_class: type[SatisfactionMeasure]
    ) -> SatisfactionProfile | SatisfactionMultiProfile:
        ...

    @abstractmethod
    def total_len(self) -> int:
        ...


class Profile(list, AbstractProfile):
    """
    A profile, that is, a list of elemnts per voters. It typically contrains all the ballots of the voters, but
    can also be a profile of satisfaction functions.
    This class inherits from `list`.
    This is the class that all profile formats inherit from.
    Attributes
    ----------
        instance : pabutools.instance.instance.PBInstance
            The instance with respect to which the profile is defined.
    """

    def __init__(
        self,
        iterable: Iterable[Ballot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = True,
        ballot_type: type[Ballot] = None,
    ) -> None:
        self.ballot_validation = ballot_validation
        self.ballot_type = ballot_type
        for item in iterable:
            self.validate_ballot(item)
        list.__init__(self, iterable)
        AbstractProfile.__init__(self)
        if instance is None:
            instance = Instance()
        self.instance = instance

    def validate_ballot(self, ballot: Ballot) -> None:
        if (
            self.ballot_validation
            and self.ballot_type is not None
            and not issubclass(type(ballot), self.ballot_type)
        ):
            raise TypeError(
                "Ballot type {} is not compatible with profile type {}.".format(
                    type(ballot), self.__class__.__name__
                )
            )

    def multiplicity(self, ballot: Ballot) -> int:
        return 1

    def as_multiprofile(self):
        ...

    def as_sat_profile(self, sat_class: type[SatisfactionMeasure]):
        return SatisfactionProfile(
            instance=self.instance, profile=self, sat_class=sat_class
        )

    def total_len(self) -> int:
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
    """ """

    def __init__(
        self,
        iterable: Iterable[FrozenBallot] = (),
        instance: Instance | None = None,
        ballot_validation: bool = True,
        ballot_type: type[FrozenBallot] = None,
    ) -> None:
        self.ballot_validation = ballot_validation
        self.ballot_type = ballot_type
        Counter.__init__(self, iterable)
        AbstractProfile.__init__(self)
        if instance is None:
            instance = Instance()
        self.instance = instance

    def validate_ballot(self, ballot: FrozenBallot) -> None:
        if (
            self.ballot_validation
            and self.ballot_type is not None
            and not issubclass(type(ballot), self.ballot_type)
        ):
            raise TypeError(
                "Ballot type {} is not compatible with profile type {}.".format(
                    type(ballot), self.__class__.__name__
                )
            )

    def multiplicity(self, ballot: FrozenBallot) -> int:
        return self[ballot]

    def as_sat_profile(self, sat_class: type[SatisfactionMeasure]):
        return SatisfactionMultiProfile(
            instance=self.instance, multiprofile=self, sat_class=sat_class
        )

    def total_len(self) -> int:
        return self.total()

    def __setitem__(self, key, value):
        self.validate_ballot(key)
        super().__setitem__(key, value)

    def append(self, element):
        if element in self:
            self[element] += 1
        else:
            self[element] = 1

    def extend(self, iterable: Iterable[FrozenBallot] | Iterable[Ballot]):
        for ballot in iterable:
            if issubclass(type(ballot), Ballot):
                self.append(ballot.frozen())
            else:
                self.append(ballot)
