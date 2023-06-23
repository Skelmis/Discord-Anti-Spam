import datetime
from unittest.mock import AsyncMock, Mock, patch

import discord
import pytest

from antispam import (
    LogicError,
    MissingGuildPermissions,
    Options,
    PropagateFailure,
    InvalidMessage,
    UnsupportedAction,
)
from antispam.dataclasses import Guild, Member, Message
from .conftest import MockClass

from .mocks import MockedMessage


# noinspection DuplicatedCode
class TestLibDPY:
    """A class devoted to testing dpy.py"""

    @pytest.mark.asyncio
    async def test_create_message_raises(self, create_dpy_lib_handler):
        message = MockedMessage().to_mock()
        message.content = None
        message.embeds = None
        message.attachments = None

        with pytest.raises(InvalidMessage):
            await create_dpy_lib_handler.create_message(message)

        with pytest.raises(InvalidMessage):
            # Test embeds that ain't embeds raise
            message.embeds = [MockClass()]
            await create_dpy_lib_handler.create_message(message)

        with pytest.raises(InvalidMessage):
            # test embed type raises
            embed = discord.Embed()
            embed.type = "Not rich"
            message.embeds = [embed]
            await create_dpy_lib_handler.create_message(message)

        with pytest.raises(InvalidMessage):
            mocked = MockedMessage().to_mock()
            mocked.is_system = Mock(return_value=True)
            await create_dpy_lib_handler.create_message(mocked)

    @pytest.mark.asyncio
    async def test_create_message_blank_space(self, create_dpy_lib_handler):
        message = MockedMessage(
            message_clean_content="u200Bu200Cu200Du200Eu200FuFEFF Hi"
        ).to_mock()

        returned_message = await create_dpy_lib_handler.create_message(message)
        assert returned_message.content == " Hi"

        create_dpy_lib_handler.handler.options.delete_zero_width_chars = False
        returned_message = await create_dpy_lib_handler.create_message(message)
        assert returned_message.content == "u200Bu200Cu200Du200Eu200FuFEFF Hi"

    @pytest.mark.asyncio
    async def test_create_message_stickers(self, create_dpy_lib_handler):
        mock_sticker = Mock()
        mock_sticker.url = "https://google.com"

        message = MockedMessage(stickers=[mock_sticker]).to_mock()

        r_1 = await create_dpy_lib_handler.create_message(message)
        assert r_1.content == "https://google.com"

    @pytest.mark.asyncio
    async def test_create_message_embed(self, create_dpy_lib_handler):
        embed = discord.Embed(title="Hello", description="world")
        mock = MockedMessage(message_clean_content=None, message_content=None).to_mock()
        mock.embeds = [embed]
        message = await create_dpy_lib_handler.create_message(mock)
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

    @pytest.mark.asyncio
    async def test_embed_to_string(self, create_dpy_lib_handler):
        embed = discord.Embed()
        assert "" == await create_dpy_lib_handler.embed_to_string(embed=embed)

        embed = discord.Embed(title="Hello", description="World")
        embed.set_footer(text="This is weird")
        embed.set_author(name="Its almost as if")
        embed.add_field(name="I am", value="Alive")
        embed.add_field(name="That would be weird tho", value="Right?")
        assert (
            "Hello\nWorld\nThis is weird\nIts almost as if\nI am\nAlive\nThat would be weird tho\nRight?\n"
            == await create_dpy_lib_handler.embed_to_string(embed)
        )

        embed = discord.Embed(title="Hello", description="World")
        embed.set_footer(icon_url="This is weird")
        embed.set_author(name="Its almost as if")
        embed.add_field(name="I am", value="Alive")
        embed.add_field(name="That would be weird tho", value="Right?")
        assert (
            "Hello\nWorld\nIts almost as if\nI am\nAlive\nThat would be weird tho\nRight?\n"
            == await create_dpy_lib_handler.embed_to_string(embed)
        )

    @pytest.mark.asyncio
    async def test_dict_to_embed(self, create_dpy_lib_handler):
        warn_embed_dict = {
            "title": "**Dear Dave**",
            "description": "You are being warned for spam, please stop!",
            "color": 0xFF0000,
            "footer": {"text": "BOT"},
            "author": {"name": "Guild"},
            "fields": [
                {"name": "Current warns:", "value": "1"},
                {"name": "Current kicks:", "value": "2", "inline": False},
            ],
        }

        mock_message = MockedMessage().to_mock()

        test_embed = await create_dpy_lib_handler.dict_to_embed(
            warn_embed_dict, mock_message, 1, 2
        )

        embed = discord.Embed(
            title="**Dear Dave**",
            description="You are being warned for spam, please stop!",
            color=0xFF0000,
        )
        embed.set_footer(text="BOT")
        embed.set_author(name="Guild")
        embed.add_field(name="Current warns:", value="1")
        embed.add_field(name="Current kicks:", value="2", inline=False)

        assert embed.to_dict() == test_embed.to_dict()

        bounds_dict = {
            "footer": {"icon_url": "$MEMBERAVATAR"},
            "author": {"icon_url": "$BOTAVATAR", "name": "d"},
            # "timestamp": True,
            "colour": 0xFFFFFF,
        }
        # mock_message.created_at = datetime.datetime.utcnow()
        mock_message.guild.me.display_avatar = "test"
        mock_message.author.display_avatar = "author"
        test_embed = await create_dpy_lib_handler.dict_to_embed(
            bounds_dict, mock_message, 1, 2
        )

        embed_two = discord.Embed(color=0xFFFFFF)
        embed_two.set_footer(icon_url="author")
        embed_two.set_author(icon_url="test", name="d")

        assert embed_two.to_dict() == test_embed.to_dict()

        bounds_dict = {
            "footer": {"icon_url": "x"},
            "author": {"icon_url": "y", "name": "d"},
            # "timestamp": True,
            "colour": 0xFFFFFF,
        }
        test_embed = await create_dpy_lib_handler.dict_to_embed(
            bounds_dict, mock_message, 1, 2
        )

        embed_two = discord.Embed(color=0xFFFFFF)
        embed_two.set_footer(icon_url="x")
        embed_two.set_author(icon_url="y", name="d")

        assert embed_two.to_dict() == test_embed.to_dict()

    @pytest.mark.asyncio
    async def test_visualizer(self, create_dpy_lib_handler):
        await create_dpy_lib_handler.visualizer("Lol", MockedMessage().to_mock())
        await create_dpy_lib_handler.visualizer(
            "{'data': 1}", MockedMessage().to_mock()
        )

    @pytest.mark.asyncio()
    async def test_propagate_type_fails(self, create_dpy_lib_handler):
        with pytest.raises(PropagateFailure):
            await create_dpy_lib_handler.check_message_can_be_propagated("lol")

    @pytest.mark.asyncio()
    async def test_delete_message_called(self, create_dpy_lib_handler):
        msg = MockedMessage().to_mock()
        msg.delete = AsyncMock(return_value=True)

        assert msg.delete.call_count == 0

        await create_dpy_lib_handler.delete_message(msg)

        assert msg.delete.call_count == 1

    @pytest.mark.asyncio
    async def test_delete_member_messages(self, create_dpy_lib_handler):
        member = Member(1, 2)
        member.messages = [
            Message(1, 2, 3, 4, "First"),
            Message(2, 2, 3, 4, "second", is_duplicate=True),
            Message(3, 2, 3, 4, "third", is_duplicate=True),
        ]

        with patch(
            "antispam.libs.dpy.DPY.delete_message", new_callable=AsyncMock
        ) as delete_call:
            await create_dpy_lib_handler.delete_member_messages(member)
            assert delete_call.call_count == 2
