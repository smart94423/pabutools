import random

from collections.abc import Iterable

from pbvoting.election.instance import Project
from pbvoting.election.ballot.ballot import Ballot, FrozenBallot


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
