from collections.abc import Iterable

from pbvoting.election.ballot import Ballot, OrdinalBallot, FrozenBallot, FrozenOrdinalBallot
from pbvoting.election.profile.profile import Profile, MultiProfile
from pbvoting.election.instance import Instance


class OrdinalProfile(Profile):
    """
    A profile of cardinal ballots. Inherits from `pbvoting.instance.profile.Profile`.
    Attributes
    ----------
    """

    def __init__(self,
                 iterable: Iterable[OrdinalBallot] = (),
                 instance: Instance | None = None,
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

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, list) and not isinstance(result, cls):
                    result = cls(result,
                                 instance=self.instance,
                                 ballot_validation=self.ballot_validation,
                                 ballot_type=self.ballot_type,
                                 legal_min_length=self.legal_min_length,
                                 legal_max_length=self.legal_max_length)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


OrdinalProfile._wrap_methods(['__add__', '__iadd__', '__imul__', '__mul__', '__reversed__', '__rmul__', 'copy',
                              'reverse'])


class OrdinalMultiProfile(MultiProfile):
    """
    """

    def __init__(self,
                 iterable: Iterable[FrozenOrdinalBallot] = (),
                 instance: Instance | None = None,
                 ballot_validation: bool = True,
                 ballot_type: type[FrozenBallot] = FrozenOrdinalBallot,
                 profile: OrdinalProfile = None,
                 legal_min_length: int | None = None,
                 legal_max_length: int | None = None
                 ) -> None:
        super(OrdinalMultiProfile, self).__init__(iterable=iterable, instance=instance,
                                                  ballot_validation=ballot_validation, ballot_type=ballot_type)
        if profile is not None:
            self.extend(profile)
        self.legal_min_length = legal_min_length
        self.legal_max_length = legal_max_length
