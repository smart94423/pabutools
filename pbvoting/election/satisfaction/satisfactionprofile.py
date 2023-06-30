from __future__ import annotations

from collections import Counter

from pbvoting.election.satisfaction.satisfactionmeasure import SatisfactionMeasure, GroupSatisfactionMeasure
from pbvoting.election.instance import Instance

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pbvoting.election.profile import Profile, MultiProfile


class SatisfactionProfile(list, GroupSatisfactionMeasure):
    """
        A profile of satisfaction functions, one per voter.
        Attributes
        ----------
    """

    def __init__(self,
                 iterable=(),
                 instance: Instance = None,
                 profile: Profile = None,
                 sat_class: type[SatisfactionMeasure] = None
                 ) -> None:
        super(SatisfactionProfile, self).__init__(iterable)
        self.instance = instance
        if profile is None:
            if sat_class is not None:
                raise TypeError("If you provide a satisfaction class, you need to also provide a profile.")
        else:
            if sat_class is None:
                raise TypeError("If you provide a profile, you need to also provide a satisfaction class.")
            else:
                self.extend_from_profile(profile, sat_class)

    def extend_from_profile(self,
                            profile: Profile = None,
                            sat_class: type[SatisfactionMeasure] = None
                            ):
        for ballot in profile:
            self.append(sat_class(self.instance, profile, ballot))

    def total_satisfaction(self, projects):
        res = 0
        for sat in self:
            res += sat.sat(projects)
        return res

    def multiplicity(self, sat: SatisfactionMeasure) -> int:
        return 1

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, list) and not isinstance(result, cls):
                    result = cls(result,
                                 instance=self.instance)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


SatisfactionProfile._wrap_methods(['__add__', '__iadd__', '__imul__', '__mul__', '__reversed__', '__rmul__', 'copy',
                               'reverse'])


class SatisfactionMultiProfile(Counter, GroupSatisfactionMeasure):
    """
        A profile of satisfaction functions, one per voter.
        Attributes
        ----------
    """

    def __init__(self,
                 d: dict[SatisfactionMeasure, int] = None,
                 instance: Instance = None,
                 profile: Profile = None,
                 multiprofile: MultiProfile = None,
                 sat_class: type[SatisfactionMeasure] = None
                 ) -> None:
        if d is None:
            d = {}
        super(SatisfactionMultiProfile, self).__init__(d)
        self.instance = instance
        if profile is None and multiprofile is None:
            if sat_class is not None:
                raise TypeError("If you provide a satisfaction class, you need to also provide a profile or a "
                                "multiprofile.")
        else:
            if sat_class is None:
                raise TypeError("If you provide a profile or a multiprofile, you need to also provide a satisfaction"
                                " class.")
            else:
                if profile is not None:
                    self.extend_from_profile(profile, sat_class)
                if multiprofile is not None:
                    self.extend_from_multiprofile(multiprofile, sat_class)

    def extend_from_profile(self, profile: Profile, sat_class: type[SatisfactionMeasure]):
        for ballot in profile:
            self.append(sat_class(self.instance, profile, ballot.frozen()))

    def extend_from_multiprofile(self, profile: MultiProfile, sat_class: type[SatisfactionMeasure]):
        for ballot, multiplicity in profile.items():
            sat = sat_class(self.instance, profile, ballot)
            if sat in self:
                self[sat] += multiplicity
            else:
                self[sat] = multiplicity

    def append(self, element):
        if element in self:
            self[element] += 1
        else:
            self[element] = 1

    def total_satisfaction(self, projects):
        res = 0
        for sat, multiplicity in self.items():
            res += multiplicity * sat.sat(projects)
        return res

    def multiplicity(self, sat: SatisfactionMeasure) -> int:
        return self[sat]
