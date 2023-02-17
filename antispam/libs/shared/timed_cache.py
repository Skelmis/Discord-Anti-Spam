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
from typing import Any, Dict, Optional, Generic, TypeVar

import attr

from antispam.exceptions import ExistingEntry, NonExistentEntry


@attr.s(slots=True)
class Entry:
    value: Any = attr.ib()
    expiry_time: Optional[datetime] = attr.ib(default=None)


KT = TypeVar("KT", bound=Any)
VT = TypeVar("VT", bound=Any)


class TimedCache(Generic[KT, VT]):
    __slots__ = ("cache", "global_ttl", "non_lazy")

    def __init__(
        self,
        *,
        global_ttl: Optional[timedelta] = None,
        lazy_eviction: bool = True,
    ):
        """
        Parameters
        ----------
        global_ttl: Optional[timedelta]
            A default TTL for any added entries.
        lazy_eviction: bool
            Whether this cache should perform lazy eviction or not.
            Defaults to True
        """
        self.cache: Dict[KT, Entry] = {}
        self.non_lazy: bool = not lazy_eviction
        self.global_ttl: Optional[timedelta] = global_ttl

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

    def __len__(self):
        self.force_clean()
        return len(self.cache.keys())

    def add_entry(
        self,
        key: KT,
        value: VT,
        *,
        ttl: Optional[timedelta] = None,
        override: bool = False,
    ) -> None:
        """
        Add an entry to the cache.
        Parameters
        ----------
        key
            The key to store this under.
        value
            The item you want to store in the cache
        ttl: Optional[timedelta]
            An optional period of time to expire
            this entry after.
        override: bool
            Whether or not to override an existing value
        Raises
        ------
        ExistingEntry
            You are trying to insert a duplicate key
        Notes
        -----
        ttl passed to this method will
        take precendence over the global ttl.
        """
        self._perform_eviction()
        if key in self and not override:
            raise ExistingEntry

        if ttl or self.global_ttl:
            ttl = ttl or self.global_ttl
            self.cache[key] = Entry(value=value, expiry_time=(datetime.now() + ttl))
        else:
            self.cache[key] = Entry(value=value)

    def delete_entry(self, key: KT) -> None:
        """
        Delete a key from the cache
        Parameters
        ----------
        key
            The key to delete
        """
        self._perform_eviction()
        try:
            self.cache.pop(key)
        except KeyError:
            pass

    def get_entry(self, key: KT) -> VT:
        """
        Fetch a value from the cache
        Parameters
        ----------
        key
            The key you wish to
            retrieve a value for
        Returns
        -------
        VT
            The provided value
        Raises
        ------
        NonExistentEntry
            No value exists in the cache
            for the provided key.
        """
        self._perform_eviction()
        if key not in self:
            raise NonExistentEntry

        return self.cache[key].value

    def force_clean(self) -> None:
        """
        Clear out all outdated cache items.
        """
        now = datetime.now()
        self.cache = {
            k: v
            for k, v in self.cache.items()
            if (v.expiry_time and v.expiry_time > now) or not v.expiry_time
        }

    def _perform_eviction(self):
        if self.non_lazy:
            self.force_clean()
