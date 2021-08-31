import logging

import discord

from antispam import PropagateFailure
from antispam.abc import Lib
from antispam.dataclasses.propagate_data import PropagateData

log = logging.getLogger(__name__)


class DPY(Lib):
    def __init__(self, handler):
        self.handler = handler

    async def check_message_can_be_propagated(
        self, message: discord.Message
    ) -> PropagateData:
        # Ensure we only moderate actual guild messages
        if not message.guild:
            log.debug("Message was not in a guild")
            raise PropagateFailure(data={"status": "Ignoring messages from dm's"})

        # The bot is immune to spam
        if message.author.id == self.handler.bot.user.id:
            log.debug("Message was from myself")
            raise PropagateFailure(
                data={"status": "Ignoring messages from myself (the bot)"}
            )

        if isinstance(message.author, discord.User):
            log.warning(f"Given message with an author of type User")

        # Return if ignored bot
        if self.handler.options.ignore_bots and message.author.bot:
            log.debug(f"I ignore bots, and this is a bot message: {message.author.id}")
            raise PropagateFailure(data={"status": "Ignoring messages from bots"})

        # Return if ignored member
        if message.author.id in self.handler.options.ignored_members:
            log.debug(f"The user who sent this message is ignored: {message.author.id}")
            raise PropagateFailure(
                data={"status": f"Ignoring this member: {message.author.id}"}
            )

        # Return if ignored channel
        if (
            message.channel.id in self.handler.options.ignored_channels
            or message.channel.name in self.handler.options.ignored_channels
        ):
            log.debug(f"{message.channel} is ignored")
            raise PropagateFailure(
                data={"status": f"Ignoring this channel: {message.channel.id}"}
            )

        # Return if member has an ignored role
        try:
            user_roles = [role.id for role in message.author.roles]
            user_roles.extend([role.name for role in message.author.roles])
            for item in user_roles:
                if item in self.handler.options.ignored_roles:
                    log.debug(f"{item} is a part of ignored roles")
                    raise PropagateFailure(
                        data={"status": f"Ignoring this role: {item}"}
                    )
        except AttributeError:
            log.warning(
                f"Could not compute ignored_roles for {message.author.name}({message.author.id})"
            )

        # Return if ignored guild
        if message.guild.id in self.handler.options.ignored_guilds:
            log.debug(f"{message.guild.id} is an ignored guild")
            raise PropagateFailure(
                data={"status": f"Ignoring this guild: {message.guild.id}"}
            )

        perms = message.guild.me.guild_permissions
        has_perms = perms.kick_members or perms.ban_members

        return PropagateData(
            guild_id=message.guild.id,
            member_name=message.author.name,
            member_id=message.author.id,
            has_perms_to_make_guild=has_perms,
        )
