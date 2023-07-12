import random

from collections.abc import Iterable

from pbvoting.election.instance import Project
from pbvoting.election.ballot.ballot import Ballot, FrozenBallot


class FrozenApprovalBallot(tuple[Project], FrozenBallot):
    def __init__(
        self,
        approved: Iterable[Project] = (),
        name: str | None = None,
        meta: dict | None = None,
    ) -> None:
        tuple.__init__(self)
        if name is None:
            if hasattr(approved, "name"):
                name = approved.name
            else:
                name = ""
        if meta is None:
            if hasattr(approved, "meta"):
                meta = approved.meta
            else:
                meta = dict
        FrozenBallot.__init__(self, name, meta)

    def __new__(
        cls, approved: Iterable[Project] = (), name: str = "", meta: dict | None = None
    ):
        return super(FrozenApprovalBallot, cls).__new__(cls, tuple(approved))

    def __hash__(self):
        return tuple.__hash__(self)


class ApprovalBallot(set[Project], Ballot):
    """
    An approval ballot, that is, a ballot in which the voter has indicated the projects that they approve of. It
    is a subclass of the Python class `set` and of the abstract class `Ballot`.
    Attributes
    ----------
        name : str
            The identifier of the ballot.
        meta : dict
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc...
    """

    def __init__(
        self,
        approved: Iterable[Project] = (),
        name: str | None = None,
        meta: dict | None = None,
    ) -> None:
        """
        Parameters
        ----------
            approved: Iterable[Project], optional (defaults to `()`)
                Approved projects
            name : str, optional (defaults to `""`)
                The identifier of the ballot.
            meta : dict, optional (defaults to `dict()`)
                Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
                strings. Could for instance store the gender of the voter, their location etc...
        """
        set.__init__(self, approved)
        if name is None:
            if hasattr(approved, "name"):
                name = approved.name
            else:
                name = ""
        if meta is None:
            if hasattr(approved, "meta"):
                meta = approved.meta
            else:
                meta = dict()
        Ballot.__init__(self, name, meta)

    def frozen(self) -> FrozenApprovalBallot:
        """
        Returns the frozen approval ballot (that is hashable) corresponding to the ballot.

        Returns
        -------
            FrozenApprovalBallot
                The frozen approval ballot
        """
        return FrozenApprovalBallot(self, name=self.name, meta=self.meta)

    # Ensures that methods returning copies of sets cast back into ApprovalBallot
    @classmethod
    def _wrap_methods(cls, methods):
        def wrap_method_closure(method):
            def inner_method(self, *args):
                result = getattr(super(cls, self), method)(*args)
                if isinstance(result, set) and not isinstance(result, cls):
                    result = cls(approved=result, name=self.name, meta=self.meta)
                return result

            inner_method.fn_name = method
            setattr(cls, method, inner_method)

        for m in methods:
            wrap_method_closure(m)


ApprovalBallot._wrap_methods(
    [
        "__ror__",
        "difference_update",
        "__isub__",
        "symmetric_difference",
        "__rsub__",
        "__and__",
        "__rand__",
        "intersection",
        "difference",
        "__iand__",
        "union",
        "__ixor__",
        "symmetric_difference_update",
        "__or__",
        "copy",
        "__rxor__",
        "intersection_update",
        "__xor__",
        "__ior__",
        "__sub__",
    ]
)


def get_random_approval_ballot(
    projects: Iterable[Project], name: str = "RandomAppBallot"
) -> ApprovalBallot:
    """
    Generates a random approval ballot in which each project is approved with probability 0.5.

    Parameters
    ----------
        projects : Iterable[Project]
            A collection of projects
        name : str, optional (defaults to `"RandomAppBallot"`)
            The identifier of the ballot.
    Returns
    -------
        ApprovalBallot
            The approval ballot
    """
    ballot = ApprovalBallot(name=name)
    for p in projects:
        if random.random() > 0.5:
            ballot.add(p)
    return ballot
