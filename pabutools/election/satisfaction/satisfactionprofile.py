"""
Satisfaction profiles.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from numbers import Number

from pabutools.election.satisfaction.satisfactionmeasure import (
    SatisfactionMeasure,
    GroupSatisfactionMeasure,
)
from pabutools.election.instance import Instance, Project
from pabutools.election.ballot.ballot import AbstractBallot

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pabutools.election.profile import Profile, MultiProfile


class SatisfactionProfile(list, GroupSatisfactionMeasure):
    """
    A profile of satisfaction measure, i.e., a collection of satisfaction measures, one per voter.
    This class inherits from the Python `list` class and can thus be used as one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            An iterable of :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure` used
            as initialize of the list.
        instance : :py:class:`~pabutools.election.instance.Instance`, optional
            The instance corresponding to the satisfaction profile.
            Defaults to `Instance()`.
        profile : :py:class:`~pabutools.election.profile.profile.Profile`
            A profile to extract the ballots from. If the `profile` argument is used, the `sat_class` argument should be
            used as well. In this case, the satisfaction profile is initialized with the satisfaction measure
            corresponding to the ballots in the profile given the satisfaction measure class passed as `sat_class`.
        sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            A satisfaction class to use for converting a potentially given profile. Can only be used if the `profile`
            argument is also used. Note that we need here the class of the satisfaction measure, and not an instance of
            it.

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance corresponding to the satisfaction profile.
        sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            The satisfaction class used to generate the satisfaction profile.
    """

    def __init__(
        self,
        init: Iterable[SatisfactionMeasure] = (),
        instance: Instance = None,
        profile: Profile = None,
        sat_class: type[SatisfactionMeasure] = None,
    ) -> None:
        list.__init__(self, init)
        GroupSatisfactionMeasure.__init__(self)
        if instance is None:
            if isinstance(init, SatisfactionProfile):
                instance = init.instance
            elif profile and profile.instance:
                instance = profile.instance
            else:
                instance = Instance()
        self.instance = instance
        if profile is None:
            if sat_class is not None:
                raise TypeError(
                    "If you provide a satisfaction class, you need to also provide a profile."
                )
        else:
            if sat_class is None:
                raise TypeError(
                    "If you provide a profile, you need to also provide a satisfaction class."
                )
            else:
                self.extend_from_profile(profile, sat_class)
        if sat_class is None and isinstance(init, SatisfactionProfile):
            self.sat_class = init.sat_class
        else:
            self.sat_class = sat_class

    def extend_from_profile(
        self, profile: Profile, sat_class: type[SatisfactionMeasure]
    ) -> None:
        """
        Extends the satisfaction profile with the profile passed as argument using the satisfaction class passed as
        argument.

        Parameters
        ----------
            profile : :py:class:`~pabutools.election.profile.profile.Profile`
                The collection of ballots to extend from.
            sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
                The satisfaction class used to convert the ballots into satisfaction measures.
        """
        for ballot in profile:
            self.append(sat_class(self.instance, profile, ballot))

    def multiplicity(self, sat: SatisfactionMeasure) -> int:
        """
        Returns 1 regardless of the input (even if the satisfaction measure does not appear in the profile,
        to save up computation).

        Parameters
        ----------
            sat : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`
                The satisfaction measure.

        Returns
        -------
            int
                1
        """
        return 1

    def remove_satisfied(
        self, sat_bound: dict[str, Number], projects: Iterable[Project]
    ) -> SatisfactionProfile:
        res = SatisfactionProfile(
            (s for s in self if s.sat(projects) < sat_bound[s.ballot.name]),
            instance=self.instance,
        )
        res.sat_class = self.sat_class
        return res

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, list) and not isinstance(result, cls):
                    result = cls(result, instance=self.instance)
                    result.sat_class = self.sat_class
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


SatisfactionProfile._wrap_methods(
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


class SatisfactionMultiProfile(Counter, GroupSatisfactionMeasure):
    """
    A multiprofile of satisfaction measure, i.e., a collection of satisfaction measures together with their
    multiplicity.
    This class inherits from the Python `Counter` class and can thus be used as one.

    Parameters
    ----------
        init : Iterable[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`] or
            dict[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`, int]
            The initialiser for the `Counter`. Can either be an iterable of
            :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure` or a mapping of
            :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure` to int.
        instance : :py:class:`~pabutools.election.instance.Instance`, optional
            The instance corresponding to the satisfaction profile.
            Defaults to `Instance()`.
        profile : :py:class:`~pabutools.election.profile.profile.Profile`
            A profile to extract the ballots from. If the `profile` argument is used, the `sat_class` argument should be
            used as well. In this case, the satisfaction profile is initialized with the satisfaction measure
            corresponding to the ballots in the profile given the satisfaction measure class passed as `sat_class`.
        multiprofile : :py:class:`~pabutools.election.profile.profile.MultiProfile`
            A multiprofile to extract the ballots from. If the `multiprofile` argument is used, the `sat_class` argument
            should be used as well. In this case, the satisfaction profile is initialized with the satisfaction measure
            corresponding to the ballots in the multiprofile given the satisfaction measure class passed as `sat_class`.
        sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            A satisfaction class to use for converting a potentially given profile. Can only be used if either the
            `profile` or the `multiprofile` argument are also used. Note that we need here the class of the
            satisfaction measure, and not an instance of it.
        inner_sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            The satisfaction class that needs to be stored in the `sat_class` attribute. Rarely useful (but needed for
            deepcopy).

    Attributes
    ----------
        instance : :py:class:`~pabutools.election.instance.Instance`
            The instance corresponding to the satisfaction profile.
        sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
            The satisfaction class used to generate the satisfaction profile.
    """

    def __init__(
        self,
        init: Iterable[SatisfactionMeasure] | dict[SatisfactionMeasure, int] = None,
        instance: Instance = None,
        profile: Profile = None,
        multiprofile: MultiProfile = None,
        sat_class: type[SatisfactionMeasure] = None,
        inner_sat_class: type[SatisfactionMeasure] = None,
    ) -> None:
        if init is None:
            init = {}
        Counter.__init__(self, init)
        GroupSatisfactionMeasure.__init__(self)
        if instance is None:
            if isinstance(init, SatisfactionMultiProfile) or isinstance(
                init, SatisfactionProfile
            ):
                instance = init.instance
            elif profile and profile.instance:
                instance = profile.instance
            elif multiprofile and multiprofile.instance:
                instance = multiprofile.instance
            else:
                instance = Instance()
        self.instance = instance
        if profile is None and multiprofile is None:
            if sat_class is not None:
                raise TypeError(
                    "If you provide a satisfaction class, you need to also provide a profile or a "
                    "multiprofile."
                )
        else:
            if sat_class is None:
                raise TypeError(
                    "If you provide a profile or a multiprofile, you need to also provide a satisfaction"
                    " class."
                )
            else:
                if profile is not None:
                    self.extend_from_profile(profile, sat_class)
                if multiprofile is not None:
                    self.extend_from_multiprofile(multiprofile, sat_class)
        if inner_sat_class:
            self.sat_class = inner_sat_class
        else:
            if sat_class is None and (
                isinstance(init, SatisfactionMultiProfile)
                or isinstance(init, SatisfactionProfile)
            ):
                self.sat_class = init.sat_class
            else:
                self.sat_class = sat_class

    def extend_from_profile(
        self, profile: Profile, sat_class: type[SatisfactionMeasure]
    ) -> None:
        """
        Extends the satisfaction multiprofile with the profile passed as argument using the satisfaction class passed as
        argument.

        Parameters
        ----------
            profile : :py:class:`~pabutools.election.profile.profile.Profile`
                The collection of ballots to extend from.
            sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
                The satisfaction class used to convert the ballots into satisfaction measures.
        """
        for ballot in profile:
            self.append(sat_class(self.instance, profile, ballot.frozen()))

    def append(self, element: SatisfactionMeasure) -> None:
        """
        Adds a satisfaction measure to the profile.

        Parameters
        ----------
            element : :py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`
                A satisfaction measure to add to the profile.
        """
        if element in self:
            self[element] += 1
        else:
            self[element] = 1

    def extend_from_multiprofile(
        self, profile: MultiProfile, sat_class: type[SatisfactionMeasure]
    ) -> None:
        """
        Extends the satisfaction multiprofile with the multiprofile passed as argument using the satisfaction class
        passed as argument.

        Parameters
        ----------
            profile : :py:class:`~pabutools.election.profile.profile.MultiProfile`
                The multiprofile to extend from.
            sat_class : type[:py:class:`~pabutools.election.satisfaction.satisfactionmeasure.SatisfactionMeasure`]
                The satisfaction class used to convert the ballots into satisfaction measures.
        """
        for ballot, multiplicity in profile.items():
            sat = sat_class(self.instance, profile, ballot)
            if sat in self:
                self[sat] += multiplicity
            else:
                self[sat] = multiplicity

    def multiplicity(self, sat: SatisfactionMeasure) -> int:
        return self[sat]

    def remove_satisfied(
        self, sat_bound: dict[AbstractBallot, Number], projects: Iterable[Project]
    ) -> SatisfactionMultiProfile:
        res = SatisfactionMultiProfile(
            {
                s: m
                for s, m in self.items()
                if s.sat(projects) < sat_bound[s.ballot.name]
            },
            instance=self.instance,
        )
        res.sat_class = self.sat_class
        return res

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(
                        result,
                        instance=self.instance,
                    )
                    result.sat_class = self.sat_class
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)

    def __reduce__(self):
        return self.__class__, (
            dict(self),
            self.instance,
            None,
            None,
            None,
            self.sat_class,
        )


SatisfactionMultiProfile._wrap_methods(
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
