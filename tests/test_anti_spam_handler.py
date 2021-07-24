import json
from unittest.mock import MagicMock, AsyncMock

import discord
import pytest
from attr import asdict
from hypothesis import given, strategies as st
from hypothesis.strategies import text
from discord.ext import commands  # noqa

from discord.ext.antispam import (
    AntiSpamHandler,
    Options,
    GuildNotFound,
    ExtensionError,
)  # noqa

from discord.ext.antispam.enums import IgnoreType, ResetType

from discord.ext.antispam.dataclasses import Guild, Member

from discord.ext.antispam.base_extension import BaseExtension
from .fixtures import create_bot, create_handler, MockClass
from .mocks import MockedMessage

"""
    How to use hypothesis
    @given(st.none(), text())
    def test_options_typing(self, create_bot, option):
        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, options=option)
    """


class TestExceptions:
    @pytest.mark.asyncio
    async def test_base(self):
        pass

    def test_initial_options(self, create_handler: AntiSpamHandler):
        """Tests the initial options are equal to the dataclass"""
        assert create_handler.options == Options()

    def test_custom_options(self, create_bot):
        """Tests custom options get set correct"""
        handler = AntiSpamHandler(create_bot, options=Options(no_punish=True))

        assert handler.options != Options()
        assert handler.options == Options(no_punish=True)

    def test_options_typing(self, create_bot):
        """Tests the handler raises on incorrect option types"""
        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, options=1)

    def test_cache_typing(self, create_bot):
        """Tests the cache typing raises on incorrect instances"""
        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, cache=MockClass())

        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, cache=MockClass)

        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, cache=1)

    def test_add_ignored_item(self, create_handler):
        """Tests the handler adds ignored items correctly"""
        # ensure they start empty
        assert create_handler.options == Options()

    def test_init_bot_raises(self, create_bot):
        with pytest.raises(ValueError):
            AntiSpamHandler(1)

        with pytest.raises(ValueError):
            AntiSpamHandler("1")

        with pytest.raises(ValueError):
            AntiSpamHandler(AntiSpamHandler(create_bot))

    def test_add_ignored_item_raises(self, create_handler):
        # Test IGNORE_TYPE
        with pytest.raises(ValueError):
            create_handler.add_ignored_item(1, 1)

        with pytest.raises(ValueError):
            create_handler.add_ignored_item(1, "1")

        with pytest.raises(ValueError):
            create_handler.add_ignored_item(1, MockClass())

        # Test ITEM
        with pytest.raises(ValueError):
            create_handler.add_ignored_item("one", IgnoreType.ROLE)

        with pytest.raises(ValueError):
            create_handler.add_ignored_item(MockClass(), IgnoreType.ROLE)

    def test_add_ignored_member(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_members) == 0
        create_handler.add_ignored_item(1, IgnoreType.MEMBER)
        assert create_handler.options.ignored_members == {1}
        assert len(create_handler.options.ignored_members) == 1

    def test_add_ignored_channel(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_channels) == 0
        create_handler.add_ignored_item(1, IgnoreType.CHANNEL)
        assert create_handler.options.ignored_channels == {1}
        assert len(create_handler.options.ignored_channels) == 1

    def test_add_ignored_guild(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_guilds) == 0
        create_handler.add_ignored_item(1, IgnoreType.GUILD)
        assert create_handler.options.ignored_guilds == {1}
        assert len(create_handler.options.ignored_guilds) == 1

    def test_add_ignored_role(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_roles) == 0
        create_handler.add_ignored_item(1, IgnoreType.ROLE)
        assert create_handler.options.ignored_roles == {1}
        assert len(create_handler.options.ignored_roles) == 1

    def test_remove_ignored_raises(self, create_handler):
        # Test IGNORE_TYPE
        with pytest.raises(ValueError):
            create_handler.remove_ignored_item(1, 1)

        with pytest.raises(ValueError):
            create_handler.remove_ignored_item(1, "1")

        with pytest.raises(ValueError):
            create_handler.remove_ignored_item(1, MockClass())

        # Test ITEM
        with pytest.raises(ValueError):
            create_handler.remove_ignored_item("one", IgnoreType.ROLE)

        with pytest.raises(ValueError):
            create_handler.remove_ignored_item(MockClass(), IgnoreType.ROLE)

    def test_remove_ignored_member(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_members) == 0
        create_handler.remove_ignored_item(1, IgnoreType.MEMBER)
        assert len(create_handler.options.ignored_members) == 0

        create_handler.add_ignored_item(1, IgnoreType.MEMBER)
        assert len(create_handler.options.ignored_members) == 1
        create_handler.remove_ignored_item(1, IgnoreType.MEMBER)
        assert len(create_handler.options.ignored_members) == 0

    def test_remove_ignored_channel(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_channels) == 0
        create_handler.remove_ignored_item(1, IgnoreType.CHANNEL)
        assert len(create_handler.options.ignored_channels) == 0

        create_handler.add_ignored_item(1, IgnoreType.CHANNEL)
        assert len(create_handler.options.ignored_channels) == 1
        create_handler.remove_ignored_item(1, IgnoreType.CHANNEL)
        assert len(create_handler.options.ignored_channels) == 0

    def test_remove_ignored_guild(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_guilds) == 0
        create_handler.remove_ignored_item(1, IgnoreType.GUILD)
        assert len(create_handler.options.ignored_guilds) == 0

        create_handler.add_ignored_item(1, IgnoreType.GUILD)
        assert len(create_handler.options.ignored_guilds) == 1
        create_handler.remove_ignored_item(1, IgnoreType.GUILD)
        assert len(create_handler.options.ignored_guilds) == 0

    def test_remove_ignored_role(self, create_handler: AntiSpamHandler):
        assert len(create_handler.options.ignored_roles) == 0
        create_handler.remove_ignored_item(1, IgnoreType.ROLE)
        assert len(create_handler.options.ignored_roles) == 0

        create_handler.add_ignored_item(1, IgnoreType.ROLE)
        assert len(create_handler.options.ignored_roles) == 1
        create_handler.remove_ignored_item(1, IgnoreType.ROLE)
        assert len(create_handler.options.ignored_roles) == 0

    @pytest.mark.asyncio
    async def test_add_guild_options_raises(self, create_handler: AntiSpamHandler):
        with pytest.raises(ValueError):
            await create_handler.add_guild_options(1, 2)

    @pytest.mark.asyncio
    async def test_add_guild_options(self, create_handler: AntiSpamHandler):
        assert len(create_handler.cache.cache) == 0

        await create_handler.add_guild_options(1, Options(no_punish=True))
        assert len(create_handler.cache.cache) == 1
        assert create_handler.cache.cache.get(1) is not None

        await create_handler.add_guild_options(1, Options(no_punish=False))

        assert create_handler.cache.cache.get(1).options == Options(no_punish=False)

    @pytest.mark.asyncio
    async def test_get_guild_options(self, create_handler: AntiSpamHandler):
        with pytest.raises(GuildNotFound):
            await create_handler.get_guild_options(1)

        await create_handler.add_guild_options(1, Options(no_punish=False))

        await create_handler.get_guild_options(1)
        assert create_handler.cache.cache.get(1).options == Options(no_punish=False)

    @pytest.mark.asyncio
    async def test_remove_custom_options(self, create_handler: AntiSpamHandler):
        await create_handler.remove_guild_options(1)  # Shouldn't raise or anything

        await create_handler.add_guild_options(1, Options(no_punish=False))
        assert create_handler.cache.cache.get(1).options == Options(no_punish=False)

        await create_handler.remove_guild_options(1)
        assert create_handler.cache.cache.get(1).options == Options()

    @pytest.mark.asyncio
    async def test_reset_member_count(self, create_handler):
        with pytest.raises(ValueError):
            await create_handler.reset_member_count(1, 1, 1)

        await create_handler.reset_member_count(1, 1, ResetType.WARN_COUNTER)

        await create_handler.cache.set_guild(Guild(id=1, options=Options()))
        await create_handler.reset_member_count(1, 1, ResetType.WARN_COUNTER)

        await create_handler.cache.set_member(Member(1, 1, warn_count=5, kick_count=6))
        await create_handler.reset_member_count(1, 1, ResetType.WARN_COUNTER)
        assert await create_handler.cache.get_member(1, 1) == Member(
            1, 1, warn_count=0, kick_count=6
        )

        await create_handler.cache.set_member(Member(1, 1, warn_count=5, kick_count=6))
        await create_handler.reset_member_count(1, 1, ResetType.KICK_COUNTER)
        assert await create_handler.cache.get_member(1, 1) == Member(
            1, 1, warn_count=5, kick_count=0
        )

    @pytest.mark.asyncio
    async def test_add_guild_log_channel_raises(self, create_handler: AntiSpamHandler):
        with pytest.raises(ValueError):
            await create_handler.add_guild_log_channel("one")

        with pytest.raises(ValueError):
            await create_handler.add_guild_log_channel({"one": 1})

    @pytest.mark.asyncio
    async def test_add_guild_log_channel(self):
        # Mock it up
        mock_channel = MagicMock()
        mock_channel.id = 2
        mock_channel.guild.id = 1

        mock_bot = MagicMock()
        mock_bot.fetch_channel = AsyncMock(return_value=mock_channel)

        assert await mock_bot.fetch_channel.called_with(1)

        handler = AntiSpamHandler(mock_bot)

        await handler.add_guild_log_channel(1)
        g = await handler.cache.get_guild(1)
        assert g.log_channel.id == 2

    @pytest.mark.asyncio
    async def test_remove_guild_log_channel(self, create_handler: AntiSpamHandler):
        await create_handler.remove_guild_log_channel(1)  # shouldnt raise

        await create_handler.cache.set_guild(Guild(1, Options(), log_channel=1))
        result = await create_handler.cache.get_guild(1)
        assert result.log_channel == 1

        await create_handler.remove_guild_log_channel(1)
        result = await create_handler.cache.get_guild(1)
        assert result.log_channel is None

    @pytest.mark.asyncio
    async def test_load_from_dict(self, create_bot):
        test_data = {
            "options": asdict(Options()),
            "guilds": [
                {
                    "id": 1,
                    "options": asdict(Options()),
                    "members": [
                        {
                            "id": 1,
                            "guild_id": 2,
                            "is_in_guild": True,
                            "warn_count": 5,
                            "kick_count": 6,
                            "duplicate_count": 7,
                            "duplicate_channel_counter_dict": {},
                            "messages": [
                                {
                                    "id": 1,
                                    "content": "Hello World!",
                                    "guild_id": 2,
                                    "author_id": 3,
                                    "channel_id": 4,
                                    "is_duplicate": True,
                                    "creation_time": "225596:21:8:3:12:5:2021",
                                }
                            ],
                        }
                    ],
                }
            ],
        }

        await AntiSpamHandler.load_from_dict(create_bot, test_data)

    @pytest.mark.asyncio
    async def test_load_from_dict_fails(self, create_bot):
        test_data = {
            "options": asdict(Options()),
            "XD": 1,
            "guilds": [
                {
                    "id": 1,
                    "options": asdict(Options()),
                    "log_channel": MockClass,
                    "members": [
                        {
                            "id": 1,
                            "guild_id": 2,
                            "is_in_guild": True,
                            "warn_count": 5,
                            "kick_count": 6,
                            "duplicate_count": 7,
                            "duplicate_channel_counter_dict": {},
                            "messages": [
                                {
                                    "id": 1,
                                    "content": "Hello World!",
                                    "guild_id": 2,
                                    "author_id": 3,
                                    "channel_id": 4,
                                    "is_duplicate": True,
                                    "creation_time": "225596:21:8:3:12:5:2021",
                                }
                            ],
                        },
                    ],
                    "Random_data": "LOL",
                }
            ],
        }

        await AntiSpamHandler.load_from_dict(
            MagicMock(side_effect=discord.HTTPException), test_data
        )

        await AntiSpamHandler.load_from_dict(create_bot, 1, raise_on_exception=False)

        with pytest.raises(TypeError):
            await AntiSpamHandler.load_from_dict(create_bot, 1)

    @pytest.mark.asyncio
    async def test_save_to_dict(self, create_handler: AntiSpamHandler):
        await create_handler.save_to_dict()

        await create_handler.cache.set_guild(Guild(1, Options()))
        data = await create_handler.save_to_dict()
        with open("tests/raw.json", "r") as file:
            stored_data = json.load(file)

        assert data == stored_data

    def test_register_extension(self, create_handler: AntiSpamHandler):
        with pytest.raises(ExtensionError):
            create_handler.register_extension(MockClass())

        class Test(BaseExtension):
            def __init__(self, invoke=True):
                self.is_pre_invoke = invoke

        assert len(create_handler.pre_invoke_extensions.values()) == 0
        create_handler.register_extension(Test())
        assert len(create_handler.pre_invoke_extensions.values()) == 1

        # Test overwrite
        with pytest.raises(ExtensionError):
            create_handler.register_extension(Test())

        create_handler.register_extension(Test(), force_overwrite=True)

        assert len(create_handler.after_invoke_extensions.values()) == 0
        create_handler.register_extension(Test(invoke=False), force_overwrite=True)
        assert len(create_handler.after_invoke_extensions.values()) == 1

    def test_unregister_extension(self, create_handler: AntiSpamHandler):
        class Test(BaseExtension):
            def __init__(self, invoke=True):
                self.is_pre_invoke = invoke

        create_handler.register_extension(Test(invoke=False))
        assert len(create_handler.after_invoke_extensions.values()) == 1
        create_handler.unregister_extension("Test")
        assert len(create_handler.after_invoke_extensions.values()) == 0

        with pytest.raises(ExtensionError):
            create_handler.unregister_extension("Invalid Extension")

        create_handler.register_extension(Test())
        assert len(create_handler.pre_invoke_extensions.values()) == 1
        create_handler.unregister_extension("Test")
        assert len(create_handler.pre_invoke_extensions.values()) == 0

    @pytest.mark.asyncio()
    async def test_propagate_exits(self):
        bot = AsyncMock()
        bot.user.id = 9
        create_handler = AntiSpamHandler(bot)

        with pytest.raises(ValueError):
            await create_handler.propagate(1)

        with pytest.raises(ValueError):
            await create_handler.propagate("2")

        with pytest.raises(ValueError):
            await create_handler.propagate(MockClass)

        return_data = await create_handler.propagate(
            MockedMessage(is_in_guild=False).to_mock()
        )
        assert return_data["status"] == "Ignoring messages from dm's"

        return_data = await create_handler.propagate(
            MockedMessage(author_id=9).to_mock()
        )
        assert return_data["status"] == "Ignoring messages from myself (the bot)"

        create_handler.options = Options(ignore_bots=True)
        return_data = await create_handler.propagate(
            MockedMessage(author_is_bot=True).to_mock()
        )
        assert return_data["status"] == "Ignoring messages from bots"
        create_handler.options = Options()

        create_handler.options.ignored_members.add(12345)
        return_data = await create_handler.propagate(MockedMessage().to_mock())
        assert return_data["status"] == "Ignoring this member: 12345"
        create_handler.options.ignored_members.discard(12345)

        create_handler.options.ignored_channels.add(98987)
        return_data = await create_handler.propagate(MockedMessage().to_mock())
        assert return_data["status"] == "Ignoring this channel: 98987"
        create_handler.options.ignored_channels.discard(98987)
