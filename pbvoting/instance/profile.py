"""
Preference profiles and voters.
"""
from collections import Counter
from collections.abc import Iterable
from fractions import Fraction
from itertools import product

import random

from pbvoting.instance.pbinstance import PBInstance, Project
from pbvoting.utils import powerset


class Ballot:
    """
        A ballot.
        This is the class that all ballot formats inherit from.
        Attributes
        ----------
            name : str
                The identifier of the ballot.
                Defaults to `""`
            meta : dict (of str)
                Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
                strings. Could for instance store the gender of the voter, their location etc...
    """

    def __init__(self, name: str = "", meta: dict | None = None):
        if meta is None:
            meta = dict()
        self.meta = meta
        self.name = name

    def freeze(self):
        pass


class Profile(list):
    """
        A profile, that is, a list of elemnts per voters. It typically contrains all the ballots of the voters, but
        can also be a profile of satisfaction functions.
        This class inherits from `list`.
        This is the class that all profile formats inherit from.
        Attributes
        ----------
            instance : pbvoting.instance.instance.PBInstance
                The instance with respect to which the profile is defined.
    """

    def __init__(self,
                 iterable: Iterable[Ballot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[Ballot] = None
                 ) -> None:
        self.ballot_validation = ballot_validation
        self.ballot_type = ballot_type
        for item in iterable:
            self.validate_ballot(item)
        super(Profile, self).__init__(iterable)
        if instance is None:
            instance = PBInstance()
        self.instance = instance

    def validate_ballot(self, ballot: Ballot) -> None:
        if self.ballot_validation and self.ballot_type is not None and not issubclass(type(ballot), self.ballot_type):
            raise TypeError("Ballot type {} is not compatible with profile type {}.".format(type(ballot),
                                                                                            self.__class__.__name__))

    def as_multiprofile(self):
        pass

    def __add__(self, value):
        return Profile(list.__add__(self, value), instance=self.instance, ballot_validation=self.ballot_validation)

    def __mul__(self, value):
        return Profile(list.__mul__(self, value), instance=self.instance, ballot_validation=self.ballot_validation)

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


class ApprovalBallot(set[Project], Ballot):
    """
        An approval ballot, that is, a ballot in which the voter has indicated the projects that they approve of. It
        is a subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
    """

    def __init__(self,
                 approved: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        set.__init__(self, approved)
        Ballot.__init__(self, name, meta)

    def freeze(self):
        return FrozenApprovalBallot(self, name=self.name, meta=self.meta)

    # This allows set method returning copies of a set to work with PBInstances
    # See https://stackoverflow.com/questions/798442/what-is-the-correct-or-best-way-to-subclass-the-python-set-class-adding-a-new
    @classmethod
    def _wrap_methods(cls, methods):
        def wrap_method_closure(method):
            def inner_method(self, *args):
                result = getattr(super(cls, self), method)(*args)
                if isinstance(result, set) and not hasattr(result, 'name'):
                    result = cls(approved=result, name=self.name, meta=self.meta)
                return result

            inner_method.fn_name = method
            setattr(cls, method, inner_method)

        for m in methods:
            wrap_method_closure(m)


ApprovalBallot._wrap_methods(['__ror__', 'difference_update', '__isub__',
                              'symmetric_difference', '__rsub__', '__and__', '__rand__', 'intersection',
                              'difference', '__iand__', 'union', '__ixor__',
                              'symmetric_difference_update', '__or__', 'copy', '__rxor__',
                              'intersection_update', '__xor__', '__ior__', '__sub__',
                              ])


class ApprovalProfile(Profile):
    """
    A profile of approval ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[ApprovalBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[Ballot] = ApprovalBallot,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_cost: Fraction | None = None,
                 legal_max_cost: Fraction | None = None):
        super(ApprovalProfile, self).__init__(iterable=iterable, instance=instance, ballot_validation=ballot_validation,
                                              ballot_type=ballot_type)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_cost = legal_min_cost
        self.legal_max_cost = legal_max_cost

    def as_multiprofile(self):
        return ApprovalMultiProfile(instance=self.instance,
                                    profile=self,
                                    ballot_validation=self.ballot_validation,
                                    ballot_type=FrozenApprovalBallot,
                                    legal_min_length=self.legal_min_length,
                                    legal_max_length=self.legal_max_length,
                                    legal_min_cost=self.legal_min_cost,
                                    legal_max_cost=self.legal_max_cost)

    def __add__(self, value):
        return ApprovalProfile(list.__add__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
                               ballot_type=self.ballot_type,
                               legal_min_length=self.legal_min_length,
                               legal_max_length=self.legal_max_length,
                               legal_min_cost=self.legal_min_cost,
                               legal_max_cost=self.legal_max_cost)

    def __mul__(self, value):
        return ApprovalProfile(list.__mul__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
                               ballot_type=self.ballot_type,
                               legal_min_length=self.legal_min_length,
                               legal_max_length=self.legal_max_length,
                               legal_min_cost=self.legal_min_cost,
                               legal_max_cost=self.legal_max_cost)

    def approval_score(self, project: Project) -> int:
        """
            Returns the approval score of a project, that is, the number of voters who approved of it.
            Parameters
            ----------
                project : pbvoting.instance.instance.Project
                    The project.
            Returns
            -------
                int
        """
        approval_score = 0
        for ballot in self:
            if project in ballot:
                approval_score += 1
        return approval_score

    def is_trivial(self) -> bool:
        """
            Tests if the profile is trivial, meaning all projects that are approved by at least one voter have a cost
            that exceeds the budget limit.
            Returns
            -------
                bool
        """
        return all(project.cost > self.instance.budget_limit for project in self.approved_projects())

    def approved_projects(self) -> set[Project]:
        """
        A set of all projects approved by at least one voter.
        Returns
        -------
            set of projects
        """
        approved_projects = set()
        for ballot in self:
            approved_projects.update(ballot)
        return approved_projects

    def is_party_list(self) -> bool:
        """
        Check whether this profile is a party-list profile.
        In a party-list profile all approval sets are either disjoint or equal.
        Returns
        -------
            bool
        """
        return all(len(b1 & b2) in (0, len(b1)) for b1 in self for b2 in self)


def get_random_approval_ballot(projects: Iterable[Project], name: str = "RandomAppBallot") -> ApprovalBallot:
    """
        Generates a random approval ballot in which each project is approved with probability 0.5.
        Parameters
        ----------
            projects : collection of pbvoting.instance.instance.Project
                The set of all the projects.
            name : str
                The identifier of the ballot. Default is `"RandomAppBallot"`.
        Returns
        -------
            pbvoting.instance.profile.ApprovalBallot
    """
    ballot = ApprovalBallot(name=name)
    for p in projects:
        if random.random() > 0.5:
            ballot.add(p)
    return ballot


def get_random_approval_profile(instance: PBInstance, num_agents: int) -> ApprovalProfile:
    """
        Generates a random approval profile in which approval ballots are such that each project is approved with
        probability 0.5.
        Parameters
        ----------
            instance : pbvoting.instance.instance.PBInstance
                The instance the profile is defined with respect to.
            num_agents : int
                The length of the profile, i.e., the number of agents..
        Returns
        -------
            pbvoting.instance.profile.ApprovalBallot
    """
    profile = ApprovalProfile(instance=instance)
    for i in range(num_agents):
        profile.append(get_random_approval_ballot(instance, name="RandomAppBallot {}".format(i)))
    return profile


def get_all_approval_profiles(instance: PBInstance, num_agents: int):
    """
        Returns a generator over all the possible profile for a given instance of a given length.
        Parameters
        ----------
            instance : pbvoting.instance.instance.PBInstance
                The instance the profile is defined with respect to.
            num_agents : int
                The length of the profile, i.e., the number of agents..
        Returns
        -------
            pbvoting.instance.profile.ApprovalBallot
    """
    return product(powerset(instance), repeat=num_agents)


class CardinalBallot(dict[Project, Fraction], Ballot):
    """
        A cardinal ballot, that is, a ballot in which the voter has indicated a score for every project. It is a
        subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
            d : dict of projects: score
                The score assigned to the projects. The keys are the projects and map to the score.
                Defaults to the empty dictionary.
    """

    def __init__(self,
                 d: dict[Project, Fraction] = None,
                 name: str = "",
                 meta: dict | None = None):
        if d is None:
            d = {}
        dict.__init__(self, d)
        Ballot.__init__(self, name=name, meta=meta)

    def complete(self, projects, default_score):
        for project in projects:
            if project not in self:
                self[project] = default_score

    def freeze(self):
        return FrozenCardinalBallot(self)


class CardinalProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[CardinalBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[Ballot] = CardinalBallot,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Fraction | None = None,
                 legal_max_score: Fraction | None = None
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

    def score(self, project: Project) -> Fraction:
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


class CumulativeBallot(CardinalBallot):
    """
        A cumulative ballot, that is, a ballot in which the voter has indicated a score for every project using a
        total number of points allocated to the voter. It is a subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
            iterable : dict of projects: score
                The score assigned to the projects. The keys are the projects and map to the score.
                Defaults to the empty dictionary.
    """

    def __init__(self,
                 d: dict[Project, Fraction] = None,
                 name: str = "",
                 meta: dict | None = None):
        if d is None:
            d = {}
        dict.__init__(self, d)
        CardinalBallot.__init__(self, name=name, meta=meta)


class CumulativeProfile(CardinalProfile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[CumulativeBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[Ballot] = CumulativeBallot,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Fraction | None = None,
                 legal_max_score: Fraction | None = None,
                 legal_min_total_score: Fraction | None = None,
                 legal_max_total_score: Fraction | None = None
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


class OrdinalBallot(dict, Ballot):

    def __init__(self,
                 iterable: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        dict.__init__(self, {e: None for e in iterable})
        Ballot.__init__(self, name=name, meta=meta)

    def append(self, element):
        self[element] = None

    def __add__(self, other):
        result = OrdinalBallot(self, name=self.name, meta=self.meta)
        for e in other:
            result[e] = None
        return result

    def index(self, element):
        i = 0
        for e in self:
            if e == element:
                return i
            i += 1
        raise ValueError("{} is not in the ballot".format(element))

    def __eq__(self, other):
        if len(self) != len(other):
            return False
        for e1, e2 in zip(self, other):
            if e1 != e2:
                return False
        return True

    def __repr__(self):
        return list(self.keys()).__repr__()

    def __str__(self):
        return list(self.keys()).__str__()


class OrdinalProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[OrdinalBallot] = (),
                 instance: PBInstance | None = None,
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


class FrozenBallot:
    """
    """

    def __init__(self, name: str = "", meta: dict | None = None):
        if meta is None:
            meta = dict()
        self.meta = meta
        self.name = name


class MultiProfile(Counter):
    """
    """

    def __init__(self,
                 iterable: Iterable[FrozenBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = None,
                 ) -> None:
        self.ballot_validation = ballot_validation
        self.ballot_type = ballot_type
        super(MultiProfile, self).__init__(iterable)
        if instance is None:
            instance = PBInstance()
        self.instance = instance

    def validate_ballot(self, ballot: FrozenBallot) -> None:
        if self.ballot_validation and self.ballot_type is not None and not issubclass(type(ballot), self.ballot_type):
            raise TypeError("Ballot type {} is not compatible with profile type {}.".format(type(ballot),
                                                                                            self.__class__.__name__))

    def __setitem__(self, key, value):
        self.validate_ballot(key)
        super().__setitem__(key, value)

    def append(self, element):
        if element in self:
            self[element] += 1
        else:
            self[element] = 1

    def append_from_profile(self, profile: Profile):
        for ballot in profile:
            self.append(self.ballot_type(ballot))


class FrozenApprovalBallot(tuple[Project], FrozenBallot):

    def __init__(self,
                 approved: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        tuple.__init__(self)
        FrozenBallot.__init__(self, name, meta)

    def __new__(cls,
                approved: Iterable[Project] = (),
                name: str = "",
                meta: dict | None = None):
        return super(FrozenApprovalBallot, cls).__new__(cls, tuple(approved))

    def __hash__(self):
        return tuple.__hash__(self)


class ApprovalMultiProfile(MultiProfile):

    def __init__(self,
                 iterable: Iterable[FrozenApprovalBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenApprovalBallot,
                 profile: ApprovalProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_cost: Fraction | None = None,
                 legal_max_cost: Fraction | None = None):
        super(ApprovalMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                   ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.append_from_profile(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_cost = legal_min_cost
        self.legal_max_cost = legal_max_cost


class FrozenCardinalBallot(dict[Project, Fraction], FrozenBallot):

    def __init__(self,
                 d: dict[Project, Fraction] = (),
                 name: str = "",
                 meta: dict | None = None):
        dict.__init__(self, d)
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))


class CardinalMultiProfile(MultiProfile):
    """
    """

    def __init__(self,
                 iterable: Iterable[FrozenCardinalBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenCardinalBallot,
                 profile: CardinalProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Fraction | None = None,
                 legal_max_score: Fraction | None = None
                 ) -> None:
        super(CardinalMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                   ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.append_from_profile(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score


class FrozenCumulativeBallot(dict[Project, Fraction], FrozenBallot):

    def __init__(self,
                 d: dict[Project, Fraction] = (),
                 name: str = "",
                 meta: dict | None = None):
        dict.__init__(self, d)
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCardinalBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))


class CumulativeMultiProfile(CardinalMultiProfile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[FrozenCumulativeBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenCumulativeBallot,
                 profile: CumulativeProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Fraction | None = None,
                 legal_max_score: Fraction | None = None,
                 legal_min_total_score: Fraction | None = None,
                 legal_max_total_score: Fraction | None = None
                 ) -> None:
        super(CumulativeMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                     ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.append_from_profile(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score
        self.legal_min_total_score = legal_min_total_score
        self.legal_max_total_score = legal_max_total_score


class FrozenOrdinalBallot(tuple[Project], FrozenBallot):

    def __init__(self,
                 approved: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        tuple.__init__(self)
        FrozenBallot.__init__(self, name, meta)

    def __new__(cls,
                approved: Iterable[Project] = (),
                name: str = "",
                meta: dict | None = None):
        if len(set(approved)) != len(approved):
            raise ValueError("Some projects are repeated in {}, this is not a valid ordinal ballot.".format(approved))
        return super(FrozenOrdinalBallot, cls).__new__(cls, tuple(approved))

    def __hash__(self):
        return tuple.__hash__(self)


class OrdinalMultiProfile(MultiProfile):
    """
    """

    def __init__(self,
                 iterable: Iterable[FrozenOrdinalBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenOrdinalBallot,
                 profile: OrdinalProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None
                 ) -> None:
        super(OrdinalMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                  ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.append_from_profile(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
