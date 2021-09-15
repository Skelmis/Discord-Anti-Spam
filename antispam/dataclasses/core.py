import attr

from typing import Dict, Any


@attr.s
class CorePayload:
    """
    The CorePayload is a dataclasses which gets returned
    within the core punishment system for this package.

    This is returned from the :py:meth:`antispam.AntiSpamHandler.propagate` method.


    Parameters
    ----------
    member_warn_count : int
        How many warns this member has at this point in time
    member_kick_count : int
        How many kicks this member has at this point in time
    member_duplicate_count : int
        How many messages this member has marked as duplicates
    member_status : str
        The status of punishment towards the member
    member_was_warned : bool
        If the default punishment handler warned this member
    member_was_kicked : bool
        If the default punishment handler kicked this member
    member_was_banned : bool
        If the default punishment handler banned this member
    member_should_be_punished_this_message : bool
        If AntiSpamHandler thinks this member should
        receive some form of punishment this message.
        Useful for :py:class:`antispam.plugins.AntiSpamTracker`
    """

    # Per user things
    member_warn_count: int = attr.ib(default=0)
    member_kick_count: int = attr.ib(default=0)
    member_duplicate_count: int = attr.ib(default=0)
    member_status: str = attr.ib(default="Unknown")
    member_was_warned: bool = attr.ib(default=False)
    member_was_kicked: bool = attr.ib(default=False)
    member_was_banned: bool = attr.ib(default=False)
    member_should_be_punished_this_message: bool = attr.ib(default=False)

    # Per channel things
    # TODO Add per channel returns

    pre_invoke_extensions: Dict[str, Any] = attr.ib(default=attr.Factory(dict))
    after_invoke_extensions: Dict[str, Any] = attr.ib(default=attr.Factory(dict))
