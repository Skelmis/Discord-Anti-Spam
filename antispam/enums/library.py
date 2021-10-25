from enum import Enum


class Library(Enum):
    """
    An enum to denote which type of API wrapper you are
    intending on using this with. Defaults to DPY.

    Notes
    -----
    DPY forks come under DPY.
    """

    DPY = 1
    HIKARI = 2
    PINCER = 3
