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
from typing import Any, Dict, List

import attr

from antispam.dataclasses.message import Message


@attr.s(slots=True)
class Member:
    """A simplistic dataclass representing a Member"""

    id: int = attr.ib(eq=True)
    guild_id: int = attr.ib(eq=True)
    warn_count: int = attr.ib(default=0, eq=False)
    kick_count: int = attr.ib(default=0, eq=False)
    times_timed_out: int = attr.ib(default=0, eq=False)
    duplicate_counter: int = attr.ib(default=1, eq=False)
    duplicate_channel_counter_dict: Dict[int, int] = attr.ib(
        default=attr.Factory(dict), eq=False
    )
    internal_is_in_guild: bool = attr.ib(default=True, eq=False)
    messages: List[Message] = attr.ib(default=attr.Factory(list), eq=False)

    # So that plugins can access this data
    # key -> Plugin.__class__.__name__
    # Value -> Whatever they want to store
    addons: Dict[str, Any] = attr.ib(default=attr.Factory(dict), eq=False)
