import asyncio
import logging
from functools import lru_cache
from typing import Optional, Union, List, Dict
from unittest.mock import AsyncMock

import pincer
from pincer.core.http import HTTPClient
from pincer.exceptions import PincerError
from pincer.objects import UserMessage, Embed
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

    async def lib_embed_as_dict(self, embed: Embed) -> Dict:
        return embed.to_dict()

    async def dict_to_lib_embed(self, data: Dict):
        return Embed.from_dict(data)

    async def get_guild_id(self, message: UserMessage) -> int:
        return message.guild_id

    async def get_channel_id(self, message: UserMessage) -> int:
        return message.channel_id

    async def get_message_mentions(self, message: UserMessage) -> List[int]:
        mentions = [m.user.id for m in message.mentions]
        mentions.extend([c.id for c in message.mention_channels])
        mentions.extend([r.id for r in message.mention_roles])
        return mentions

    async def get_channel_from_message(self, message: UserMessage):
        return await self.get_channel_by_id(message.channel_id)

    async def get_channel_by_id(self, channel_id: int):
        # TODO Make this nicer?
        return await self.bot.get_channel(channel_id)

    async def get_substitute_args(self, message: UserMessage) -> SubstituteArgs:
        client: pincer.Client = self.bot
        guild: objects.Guild = await objects.Guild.from_id(client, message.guild_id)

        return SubstituteArgs(
            bot_id=client.bot.id,
            bot_name=client.bot.username,
            bot_avatar=client.bot.avatar,
            guild_id=message.guild_id,
            guild_icon=guild.icon,
            guild_name=guild.name,
            member_id=message.author.id,
            member_name=message.author.username,
            member_avatar=message.author.avatar,
        )

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
