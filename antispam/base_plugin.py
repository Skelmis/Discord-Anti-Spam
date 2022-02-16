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
from typing import Any, Dict, Optional, Set

from antispam.dataclasses import CorePayload


class BasePlugin:
    def __init__(self, is_pre_invoke=True) -> None:
        self.is_pre_invoke = is_pre_invoke

        # A set of blacklisted guilds,
        # If a guilds in this, the plugin wont run
        self.blacklisted_guilds: Set[int] = set()

    async def propagate(self, message, data: Optional[CorePayload] = None) -> Any:
        """
        This method is called whenever the base ``antispam.propagate`` is called,
        adhering to ``self.is_pre_invoke``

        Parameters
        ----------
        message : Union[discord.Message, hikari.messages.Message]
            The message to run propagation on
        data : Optional[CorePayload]
            Optional input given to after invoke plugins
            which is the return value from the main `propagate()`

        Returns
        -------
        dict
            A dictionary of useful data to the end user

        """
        raise NotImplementedError

    async def save_to_dict(self) -> Dict:
        """
        Saves the plugins state to a Dict

        Returns
        -------
        Dict
            The current plugin state as a dictionary.
        """
        raise NotImplementedError

    @classmethod
    async def load_from_dict(cls, anti_spam_handler, data: Dict):
        """
        Loads this plugin from a saved state.

        Parameters
        ----------
        anti_spam_handler: AntiSpamHandler
            The AntiSpamHandler instance
        data: Dict
            The data to load the plugin from
        """
        raise NotImplementedError
