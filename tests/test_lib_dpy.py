import datetime
from unittest.mock import AsyncMock

import discord
import pytest

from antispam.dataclasses import Guild, Member, CorePayload, Message

from antispam import Options, LogicError, MissingGuildPermissions
from .fixtures import (
    create_bot,
    create_handler,
    create_memory_cache,
    create_dpy_lib_handler,
    MockClass,
    create_dpy_lib_handler,
)
from .mocks import MockedMessage


# noinspection DuplicatedCode
class TestLibDPY:
    """A class devoted to testing core.py"""

    def test_create_message_raises(self, create_dpy_lib_handler):
        message = MockedMessage().to_mock()
        message.content = None
        message.embeds = None

        with pytest.raises(LogicError):
            create_dpy_lib_handler.create_message(message)

        with pytest.raises(LogicError):
            # Test embeds that ain't embeds raise
            message.embeds = [MockClass()]
            create_dpy_lib_handler.create_message(message)

        with pytest.raises(LogicError):
            # test embed type raises
            embed = discord.Embed()
            embed.type = "Not rich"
            message.embeds = [embed]
            create_dpy_lib_handler.create_message(message)

    def test_create_message_blank_space(self, create_dpy_lib_handler):
        message = MockedMessage(
            message_clean_content=u"u200Bu200Cu200Du200Eu200FuFEFF Hi"
        ).to_mock()

        returned_message = create_dpy_lib_handler.create_message(message)
        assert returned_message.content == " Hi"

        create_dpy_lib_handler.handler.options.delete_zero_width_chars = False
        returned_message = create_dpy_lib_handler.create_message(message)
        assert returned_message.content == u"u200Bu200Cu200Du200Eu200FuFEFF Hi"

    def test_create_message_embed(self, create_dpy_lib_handler):
        embed = discord.Embed(title="Hello", description="world")
        mock = MockedMessage(message_clean_content=None, message_content=None).to_mock()
        mock.embeds = [embed]
        message = create_dpy_lib_handler.create_message(mock)
        assert message.content == "Hello\nworld\n"

    @pytest.mark.asyncio
    async def test_punish_member_raises(self, create_dpy_lib_handler):
        with pytest.raises(MissingGuildPermissions):
            # Test kick has kick perms
            message = MockedMessage(author_id=1, guild_id=1).to_mock()
            message.guild.me.guild_permissions.kick_members = False
            await create_dpy_lib_handler.punish_member(
                message,
                Member(1, 1),
                Guild(1, Options()),
                "test user",
                "test guild",
                True,
            )

        with pytest.raises(MissingGuildPermissions):
            # Test ban has ban perms
            message = MockedMessage(author_id=1, guild_id=1).to_mock()
            message.guild.me.guild_permissions.ban_members = False
            await create_dpy_lib_handler.punish_member(
                message,
                Member(1, 1),
                Guild(1, Options()),
                "test user",
                "test guild",
                False,
            )

        with pytest.raises(MissingGuildPermissions):
            # Check errors on guild owner
            message = MockedMessage(author_id=1, guild_id=1).to_mock()
            message.guild.owner_id = 1

            await create_dpy_lib_handler.punish_member(
                message,
                Member(1, 1),
                Guild(1, Options()),
                "test user",
                "test guild",
                True,
            )

    @pytest.mark.asyncio
    async def test_punish_member(self, create_dpy_lib_handler):
        """Adds test coverage"""
        await create_dpy_lib_handler.punish_member(
            MockedMessage(author_id=1, guild_id=1).to_mock(),
            Member(1, 1),
            Guild(1, Options()),
            "test user",
            "test guild",
            True,
        )
