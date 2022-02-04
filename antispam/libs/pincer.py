import asyncio
import logging
from functools import lru_cache
from typing import Optional, Union, List, Dict
from unittest.mock import AsyncMock

import pincer
from pincer.core.http import HTTPClient
from pincer.exceptions import PincerError
from pincer.objects.guild import TextChannel

from antispam import (
    InvalidMessage,
    LogicError,
    PropagateFailure,
    MissingGuildPermissions,
)
from antispam.abc import Lib
from antispam.dataclasses import Member, Guild, Message
from antispam.dataclasses.propagate_data import PropagateData

from pincer import objects

from antispam.libs.shared import SubstituteArgs, Base

log = logging.getLogger(__name__)


class Pincer(Base, Lib):
    def __init__(self, handler):
        self.handler = handler
        self.bot: pincer.Client = self.handler.bot

    async def get_substitute_args(self, message) -> SubstituteArgs:
        raise NotImplementedError

    async def lib_embed_as_dict(self, embed) -> Dict:
        raise NotImplementedError

    async def dict_to_lib_embed(self, data: Dict):
        raise NotImplementedError

    async def get_guild_id(self, message) -> int:
        raise NotImplementedError

    async def get_channel_id(self, message) -> int:
        raise NotImplementedError

    async def get_message_mentions(self, message) -> List[int]:
        raise NotImplementedError

    async def get_channel_from_message(self, message):
        raise NotImplementedError

    async def get_channel_by_id(self, channel_id: int):
        raise NotImplementedError

    async def check_message_can_be_propagated(self, message) -> PropagateData:
        raise NotImplementedError

    async def create_message(self, message) -> Message:
        raise NotImplementedError

    async def send_guild_log(
        self,
        guild,
        message,
        delete_after_time: Optional[int],
        original_channel,
        file=None,
    ) -> None:
        raise NotImplementedError

    async def punish_member(
        self,
        original_message,
        member: Member,
        internal_guild: Guild,
        user_message,
        guild_message,
        is_kick: bool,
        user_delete_after: int = None,
        channel_delete_after: int = None,
    ):
        raise NotImplementedError

    async def delete_member_messages(self, member: Member) -> None:
        raise NotImplementedError

    async def delete_message(self, message) -> None:
        raise NotImplementedError

    async def send_message_to_(
        self, target, message, mention: str, delete_after_time: Optional[int] = None
    ) -> None:
        raise NotImplementedError
