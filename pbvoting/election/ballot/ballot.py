from abc import ABC, abstractmethod


class Ballot(ABC):
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

    @abstractmethod
    def freeze(self):
        ...


class FrozenBallot(ABC):
    """
    """

    def __init__(self, name: str = "", meta: dict | None = None):
        if meta is None:
            meta = dict()
        self.meta = meta
        self.name = name

