import logging
from typing import Optional, List, Dict

import pincer
from pincer.objects import UserMessage, Embed

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
        return await objects.TextChannel.from_id(self.bot, channel_id)

    async def get_substitute_args(self, message) -> SubstituteArgs:
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

    async def delete_member_messages(self, member: Member) -> None:
        log.debug(
            "Attempting to delete all duplicate messages for Member(id=%s) in Guild(%s)",
            member.id,
            member.guild_id,
        )
        client: pincer.Client = self.bot
        for message in member.messages:
            if not message.is_duplicate:
                continue

            actual_message: UserMessage = await UserMessage.from_id(
                client, message.id, message.channel_id
            )
            await actual_message.delete()

    async def delete_message(self, message) -> None:
        # This has no error handling under the hood.
        await message.delete()

    async def create_message(self, message: UserMessage) -> Message:
        log.debug(
            "Attempting to create a new message for author(id=%s) in Guild(%s)",
            message.author.id,
            message.guild_id,
        )
        # TODO Add
        # if message.is_system():
        #     raise InvalidMessage(
        #         "Message is a system one, we don't check against those."
        #     )

        content = ""
        if message.sticker_items:
            # 'sticker' names should be unique..
            all_stickers = "|".join(s.name for s in message.sticker_items)
            content += all_stickers

        elif not bool(message.content and message.content.strip()):
            if not message.embeds and not message.attachments:
                raise LogicError

            if not message.embeds:
                # We don't check against attachments
                raise InvalidMessage

            for embed in message.embeds:
                if not isinstance(embed, objects.Embed):
                    raise LogicError

                content += await self.embed_to_string(embed)
        else:
            content += message.content

        if self.handler.options.delete_zero_width_chars:
            content = (
                content.replace("u200B", "")
                .replace("u200C", "")
                .replace("u200D", "")
                .replace("u200E", "")
                .replace("u200F", "")
                .replace("uFEFF", "")
            )

        return Message(
            id=message.id,
            channel_id=message.channel_id,
            guild_id=message.guild_id,
            author_id=message.author.id,
            content=content,
        )

    async def send_message_to_(
        self, target, message, mention: str, delete_after_time: Optional[int] = None
    ) -> None:
        raise NotImplementedError

    async def check_message_can_be_propagated(self, message) -> PropagateData:
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
