from pabutools.election.ballot.ballot import FrozenBallot, AbstractBallot
from pabutools.election.ballot.cardinalballot import CardinalBallot
from pabutools.election.instance import Project

from numbers import Number


class FrozenCumulativeBallot(dict[Project, Number], FrozenBallot):
    """
    Frozen cumulative ballot, that is, a ballot in which the voter assigned scores to projects using a total number of
    points allocated to the voter. This is a special type of cardinal ballot
    (see :py:class:`~pabutools.election.ballot.cardinalballot.CardinalBallot`).
    Since there is not frozen dictionary implemented in Python, this class simply
    inherits from the Python class `dict`, overriding the `set_item` method to ensure that it is non-mutable
    (raising an exception if the method is used).

    Parameters
    ----------
        d: dict[:py:class:`~pabutools.election.instance.Project`], optional
            Dictionary of :py:class:`~pabutools.election.instance.Project` used to initialise the ballot. In case an
            :py:class:`~pabutools.election.ballot.ballot.AbstractBallot` object is passed, the
            additional attributes are also copied (except if the corresponding keyword arguments have been given).
            Defaults to `()`.
        name : str, optional
            The identifier of the ballot.
            Defaults to `""`.
        meta : dict, optional
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
            Defaults to `dict()`.

    Attributes
    ----------
        name : str
            The identifier of the ballot.
        meta : dict
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
    """

    def __init__(
        self,
        d: dict[Project, Number] = None,
        name: str | None = None,
        meta: dict | None = None,
    ):
        if d is None:
            d = dict()
        dict.__init__(self, d)
        if name is None:
            if isinstance(d, AbstractBallot):
                name = d.name
            else:
                name = ""
        if meta is None:
            if isinstance(d, AbstractBallot):
                meta = d.meta
            else:
                meta = dict
        FrozenBallot.__init__(self, name=name, meta=meta)

    def __setitem__(self, key, value):
        raise ValueError("You cannot set values of a FrozenCumulativeBallot")

    def __hash__(self):
        return tuple.__hash__(tuple(self.keys()))


class CumulativeBallot(CardinalBallot):
    """
    Cumulative ballot, that is, a ballot in which the voter assigned scores to projects using a total number of
    points allocated to the voter. This is a special type of cardinal ballot
    (see :py:class:`~pabutools.election.ballot.cardinalballot.CardinalBallot`).This class inherits from the
    Python class `dict` and can be used as one.

    Parameters
    ----------
        d: dict[:py:class:`~pabutools.election.instance.Project`], optional
            Dictionary of :py:class:`~pabutools.election.instance.Project` used to initialise the ballot. In case an
            :py:class:`~pabutools.election.ballot.ballot.AbstractBallot` object is passed, the
            additional attributes are also copied (except if the corresponding keyword arguments have been given).
            Defaults to `()`.
        name : str, optional
            The identifier of the ballot.
            Defaults to `""`.
        meta : dict, optional
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
            Defaults to `dict()`.

    Attributes
    ----------
        name : str
            The identifier of the ballot.
        meta : dict
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc.
    """

    def __init__(
        self,
        d: dict[Project, Number] = None,
        name: str | None = None,
        meta: dict | None = None,
    ):
        if d is None:
            d = dict()
        if name is None:
            if isinstance(d, AbstractBallot):
                name = d.name
            else:
                name = ""
        if meta is None:
            if isinstance(d, AbstractBallot):
                meta = d.meta
            else:
                meta = dict
        CardinalBallot.__init__(self, d, name=name, meta=meta)

    def frozen(self) -> FrozenCumulativeBallot:
        """
        Returns the frozen cumulative ballot (that is hashable) corresponding to the ballot.

        Returns
        -------
            FrozenCumulativeBallot
                The frozen cardinal ballot.
        """
        return FrozenCumulativeBallot(self)

    @classmethod
    def _wrap_methods(cls, names):
        def wrap_method_closure(name):
            def inner(self, *args):
                result = getattr(super(cls, self), name)(*args)
                if isinstance(result, dict) and not isinstance(result, cls):
                    result = cls(result, name=self.name, meta=self.meta)
                return result

            inner.fn_name = name
            setattr(cls, name, inner)

        for n in names:
            wrap_method_closure(n)


CumulativeBallot._wrap_methods(["copy", "__ior__", "__or__", "__ror__", "__reversed__"])
