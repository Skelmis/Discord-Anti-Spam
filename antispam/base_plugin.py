from typing import Optional

from .dataclasses import CorePayload


class BasePlugin:
    def __init__(self, is_pre_invoke=True) -> None:
        self.is_pre_invoke = is_pre_invoke

    async def propagate(self, message, data: Optional[CorePayload] = None) -> dict:
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
