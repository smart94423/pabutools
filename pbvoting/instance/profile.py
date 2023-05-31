"""
Preference profiles and voters.
"""

import random

from itertools import combinations_with_replacement

from pbvoting.instance.pbinstance import PBInstance
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

    def __init__(self, name="", meta=None):
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

    def __init__(self, iterable=(), instance=None):
        super(Profile, self).__init__(iterable)
        if instance is None:
            instance = PBInstance()
        self.instance = instance

    def __add__(self, value):
        return Profile(list.__add__(self, value), instance=self.instance)

    def __mul__(self, value):
        return Profile(list.__mul__(self, value), instance=self.instance)

    # def __getitem__(self, item):
    #     result = list.__getitem__(self, item)
    #     try:
    #         return Profile(result, instance=self.instance)
    #     except TypeError:
    #         return result


class ApprovalBallot(set, Ballot):
    """
        An approval ballot, that is, a ballot in which the voter has indicated the projects that they approve of. It
        is a subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
            approved : collection of projects
                The approved projects.
                Defaults to the empty set.
    """

    def __init__(self, approved=(), name="", meta=None):
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

    def __init__(self, iterable=(), instance=None):
        super(ApprovalProfile, self).__init__(iterable=iterable, instance=instance)

    def approval_score(self, project):
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

    def is_trivial(self):
        """
            Tests if the profile is trivial, meaning all projects that are approved by at least one voter have a cost
            that exceeds the budget limit.
            Returns
            -------
                bool
        """
        return all(project.cost > self.instance.budget_limit for project in self.approved_projects())

    def approved_projects(self):
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

    def is_party_list(self):
        """
        Check whether this profile is a party-list profile.
        In a party-list profile all approval sets are either disjoint or equal.
        Returns
        -------
            bool
        """
        return all(len(b1 & b2) in (0, len(b1)) for b1 in self for b2 in self)


def get_random_approval_ballot(projects, name="RandomAppBallot"):
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


def get_random_approval_profile(instance, num_agents):
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


def get_all_approval_profiles(instance, num_agents):
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
    return combinations_with_replacement(powerset(instance.projects), num_agents)


class CardinalBallot(dict, Ballot):
    """
        A cardinal ballot, that is, a ballot in which the voter has indicated a score for every project. It is a
        subclass of `pbvoting.instance.profile.Ballot`.
        Attributes
        ----------
            iterable : dict of projects: score
                The score assigned to the projects. The keys are the projects and map to the score.
                Defaults to the empty dictionary.
    """

    def __init__(self, iterable=(), name="", meta=None):
        dict.__init__(self, iterable)
        Ballot.__init__(self, name=name, meta=meta)


class CardinalProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self, iterable=(), instance=None):
        super(CardinalProfile, self).__init__(iterable=iterable, instance=instance)


class CumulativeProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self, iterable=(), instance=None):
        super(CumulativeProfile, self).__init__(iterable=iterable, instance=instance)


class OrdinalBallot(list, Ballot):
    def __init__(self, iterable=(), name="", meta=None):
        list.__init__(self, iterable)
        Ballot.__init__(self, name=name, meta=meta)

    def __add__(self, value):
        return OrdinalBallot(list.__add__(self, value))

    def __mul__(self, value):
        return OrdinalBallot(list.__mul__(self, value))

    def __getitem__(self, item):
        result = list.__getitem__(self, item)
        try:
            return OrdinalBallot(result)
        except TypeError:
            return result


class OrdinalProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self, iterable=(), instance=None):
        super(OrdinalProfile, self).__init__(iterable=iterable, instance=instance)

