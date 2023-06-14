"""
Preference profiles and voters.
"""

from fractions import Fraction
import random

from collections.abc import Iterable, Generator
from itertools import combinations_with_replacement, product

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
                 ballot_validation: bool = True
                 ) -> None:
        super(Profile, self).__init__(iterable)
        if instance is None:
            instance = PBInstance()
        self.instance = instance
        self.ballot_validation = ballot_validation
        self.ballot_type = None

    def validate_ballot(self, ballot: Ballot) -> None:
        if self.ballot_validation and self.ballot_type is not None and not issubclass(type(ballot), self.ballot_type):
            raise TypeError("Ballot type {} is not compatible with profile type {}.".format(type(ballot),
                                                                                            self.__class__.__name__))

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

    def extend(self, other: 'Profile') -> None:
        if isinstance(other, type(self)):
            super().extend(other)
        else:
            super().extend(item for item in other)


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

    # This allows set method returning copies of a set to work with PBInstances
    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, set) and not hasattr(result, 'foo'):
                    result = cls(approved=result, name=self.name, meta=self.meta)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


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
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_cost: Fraction | None = None,
                 legal_max_cost: Fraction | None = None):
        super(ApprovalProfile, self).__init__(iterable=iterable, instance=instance, ballot_validation=ballot_validation)
        self.ballot_type = ApprovalBallot
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_cost = legal_min_cost
        self.legal_max_cost = legal_max_cost

    def __add__(self, value):
        return ApprovalProfile(list.__add__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
                               legal_min_length=self.legal_min_length,
                               legal_max_length=self.legal_max_length,
                               legal_min_cost=self.legal_min_cost,
                               legal_max_cost=self.legal_max_cost)

    def __mul__(self, value):
        return ApprovalProfile(list.__mul__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
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
                 d: dict[Project, Fraction] = (),
                 name: str = "",
                 meta: dict | None = None):
        dict.__init__(self, d)
        Ballot.__init__(self, name=name, meta=meta)


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
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Fraction | None = None,
                 legal_max_score: Fraction | None = None
                 ) -> None:
        super(CardinalProfile, self).__init__(iterable=iterable, instance=instance, ballot_validation=ballot_validation)
        self.ballot_type = CardinalBallot
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score

    def __add__(self, value):
        return CardinalProfile(list.__add__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
                               legal_min_length=self.legal_min_length,
                               legal_max_length=self.legal_max_length,
                               legal_min_score=self.legal_min_score,
                               legal_max_score=self.legal_max_score)

    def __mul__(self, value):
        return CardinalProfile(list.__mul__(self, value), instance=self.instance,
                               ballot_validation=self.ballot_validation,
                               legal_min_length=self.legal_min_length,
                               legal_max_length=self.legal_max_length,
                               legal_min_score=self.legal_min_score,
                               legal_max_score=self.legal_max_score)


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
                 iterable: Iterable[dict[Project, Fraction]] = (),
                 name: str = "",
                 meta: dict | None = None):
        dict.__init__(self, iterable)
        CardinalBallot.__init__(self, name=name, meta=meta)


class CumulativeProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[CumulativeBallot] = (),
                 instance: PBInstance | None = None,
                 ballot_validation: bool = True,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None,
                 legal_min_score: Fraction | None = None,
                 legal_max_score: Fraction | None = None,
                 legal_min_total_score: Fraction | None = None,
                 legal_max_total_score: Fraction | None = None
                 ) -> None:
        super(CumulativeProfile, self).__init__(iterable=iterable, instance=instance,
                                                ballot_validation=ballot_validation)
        self.ballot_type = CumulativeBallot

        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
        self.legal_min_score = legal_min_score
        self.legal_max_score = legal_max_score
        self.legal_min_total_score = legal_min_total_score
        self.legal_max_total_score = legal_max_total_score

    def __add__(self, value):
        return CumulativeProfile(list.__add__(self, value), instance=self.instance,
                                 ballot_validation=self.ballot_validation,
                                 legal_min_length=self.legal_min_length,
                                 legal_max_length=self.legal_max_length,
                                 legal_min_score=self.legal_min_score,
                                 legal_max_score=self.legal_max_score,
                                 legal_min_total_score=self.legal_min_total_score,
                                 legal_max_total_score=self.legal_max_total_score)

    def __mul__(self, value):
        return CumulativeProfile(list.__mul__(self, value), instance=self.instance,
                                 ballot_validation=self.ballot_validation,
                                 legal_min_length=self.legal_min_length,
                                 legal_max_length=self.legal_max_length,
                                 legal_min_score=self.legal_min_score,
                                 legal_max_score=self.legal_max_score,
                                 legal_min_total_score=self.legal_min_total_score,
                                 legal_max_total_score=self.legal_max_total_score)


class OrdinalBallot(list, Ballot):
    def __init__(self,
                 iterable: Iterable[Project] = (),
                 name: str = "",
                 meta: dict | None = None
                 ) -> None:
        list.__init__(self, iterable)
        Ballot.__init__(self, name=name, meta=meta)

    def __add__(self, value):
        return OrdinalBallot(list.__add__(self, value), name=self.name, meta=self.meta)

    def __mul__(self, value):
        return OrdinalBallot(list.__mul__(self, value), name=self.name, meta=self.meta)


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
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None
                 ) -> None:
        super(OrdinalProfile, self).__init__(iterable=iterable, instance=instance, ballot_validation=ballot_validation)
        self.ballot_type = OrdinalBallot

        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length

    def __add__(self, value):
        return OrdinalProfile(list.__add__(self, value), instance=self.instance,
                              ballot_validation=self.ballot_validation,
                              legal_min_length=self.legal_min_length,
                              legal_max_length=self.legal_max_length)

    def __mul__(self, value):
        return OrdinalProfile(list.__mul__(self, value), instance=self.instance,
                              ballot_validation=self.ballot_validation,
                              legal_min_length=self.legal_min_length,
                              legal_max_length=self.legal_max_length)
