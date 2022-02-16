"""
The MIT License (MIT)

Copyright (c) 2020-Current Skelmis

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""
from typing import Any, Dict

import attr


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
    member_was_timed_out : bool
        If the default punishment handler timed out this member
    member_should_be_punished_this_message : bool
        If AntiSpamHandler thinks this member should
        receive some form of punishment this message.
        Useful for ``antispam.plugins.AntiSpamTracker``
    """

    # Per user things
    member_warn_count: int = attr.ib(default=0)
    member_kick_count: int = attr.ib(default=0)
    member_duplicate_count: int = attr.ib(default=0)
    member_status: str = attr.ib(default="Unknown")
    member_was_warned: bool = attr.ib(default=False)
    member_was_kicked: bool = attr.ib(default=False)
    member_was_banned: bool = attr.ib(default=False)
    member_was_timed_out: bool = attr.ib(default=False)
    member_should_be_punished_this_message: bool = attr.ib(default=False)

    # Per channel things
    # TODO Add per channel returns

    pre_invoke_extensions: Dict[str, Any] = attr.ib(default=attr.Factory(dict))
    after_invoke_extensions: Dict[str, Any] = attr.ib(default=attr.Factory(dict))
