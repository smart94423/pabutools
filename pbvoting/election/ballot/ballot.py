from abc import ABC, abstractmethod


class AbstractBallot(ABC):
    """
    Abstract class representing the ballots, i.e., the information submitted by the voters.
    """


class FrozenBallot(AbstractBallot):
    """
    Abstract class representing frozen ballots, i.e., ballots that are hashable. In general the Ballot class
    should be preferred over this one but hashable ballots can be useful (typically for `MultiProfile`).

    Attributes
    ----------
        name : str
            The identifier of the ballot.
        meta : dict
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc...
    """

    def __init__(self, name: str = "", meta: dict | None = None):
        """
        Parameters
        ----------
            name : str, optional (defaults to `""`)
                The identifier of the ballot.
            meta : dict, optional (defaults to `dict()`)
                Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
                strings. Could for instance store the gender of the voter, their location etc...
        """
        AbstractBallot.__init__(self)
        if meta is None:
            meta = dict()
        self.meta = meta
        self.name = name


class Ballot(AbstractBallot):
    """
    Abstract class representing the ballots, i.e., the information submitted by the voters.

    Attributes
    ----------
        name : str
            The identifier of the ballot.
        meta : dict
            Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
            strings. Could for instance store the gender of the voter, their location etc...
    """

    def __init__(self, name: str = "", meta: dict | None = None):
        """
        Parameters
        ----------
            name : str, optional (defaults to `""`)
                The identifier of the ballot.
            meta : dict, optional (defaults to `dict()`)
                Additional information concerning the ballot, stored in a dictionary. Keys and values are typically
                strings. Could for instance store the gender of the voter, their location etc...
        """
        AbstractBallot.__init__(self)
        if meta is None:
            meta = dict()
        self.meta = meta
        self.name = name

    @abstractmethod
    def frozen(self) -> FrozenBallot:
        """
        Returns the ballot in its frozen form, that is, as a Frozen (hashable) ballot.

        Returns
        -------
            FrozenBallot
                The ballot in its frozen form.
        """
        ...
