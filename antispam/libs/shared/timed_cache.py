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
# Taken from https://github.com/Skelmis/DPY-Bot-Base/tree/master/bot_base/caches
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import attr

from antispam.exceptions import ExistingEntry, NonExistentEntry


@attr.s(slots=True)
class Entry:
    value: Any = attr.ib()
    expiry_time: Optional[datetime] = attr.ib(default=None)


class TimedCache:
    __slots__ = ("cache",)

    def __init__(self):
        self.cache: Dict[Any, Entry] = {}

    def __contains__(self, item: Any) -> bool:
        try:
            entry = self.cache[item]
            if entry.expiry_time and entry.expiry_time < datetime.now():
                self.delete_entry(item)
                return False
        except KeyError:
            return False
        else:
            return True

    def add_entry(
        self, key: Any, value: Any, *, ttl: timedelta = None, override: bool = False
    ) -> None:
        if key in self and not override:
            raise ExistingEntry

        self.cache[key] = (
            Entry(value=value, expiry_time=(datetime.now() + ttl))
            if ttl
            else Entry(value=value)
        )

    def delete_entry(self, key: Any) -> None:
        try:
            self.cache.pop(key)
        except KeyError:
            pass

    def get_entry(self, key: Any) -> Any:
        if key not in self:
            raise NonExistentEntry

        return self.cache[key].value

    def force_clean(self) -> None:
        now = datetime.now()
        for k, v in deepcopy(self.cache).items():
            if v.expiry_time and v.expiry_time < now:
                self.delete_entry(k)
