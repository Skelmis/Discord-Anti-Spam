import json
import os.path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock

import discord
import nextcord
import pytest
from attr import asdict
from discord.ext import commands  # noqa
from hypothesis import given
from hypothesis import strategies as st
from hypothesis.strategies import text

from antispam import GuildNotFound, UnsupportedAction  # noqa
from antispam import (
    AntiSpamHandler,
    InvocationCancelled,
    MissingGuildPermissions,
    Options,
    PluginError,
    PropagateFailure,
)
from antispam.base_plugin import BasePlugin
from antispam.caches import MemoryCache
from antispam.caches.mongo import MongoCache
from antispam.dataclasses import CorePayload, Guild, Member, Message
from antispam.enums import IgnoreType, Library, ResetType
from antispam.libs.dpy import DPY
from antispam.libs.dpy_forks.lib_disnake import Disnake
from antispam.libs.dpy_forks.lib_enhanced_dpy import EnhancedDPY
from antispam.libs.dpy_forks.lib_nextcord import Nextcord
from antispam.libs.lib_hikari import Hikari
from antispam.plugins import Stats as StatsPlugin
from .conftest import MockClass

from .mocks import MockedMember, MockedMessage

"""
    How to use hypothesis
    @given(st.none(), text())
    def test_options_typing(self, create_bot, option):
        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, options=option)
    """


class TestAntiSpamHandler:
    @pytest.mark.asyncio
    async def test_base(self):
        pass

    def test_initial_options(self, create_handler: AntiSpamHandler):
        """Tests the initial options are equal to the dataclass"""
        # We hard set tests to NOT use timeouts, saves writing em all.
        assert create_handler.options == Options(use_timeouts=False)

    def test_custom_options(self, create_bot):
        """Tests custom options get set correct"""
        handler = AntiSpamHandler(
            create_bot, Library.DPY, options=Options(no_punish=True)
        )

        assert handler.options != Options()
        assert handler.options == Options(no_punish=True)

    def test_options_typing(self, create_bot):
        """Tests the handler raises on incorrect option types"""
        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, Library.DPY, options=1)

    def test_cache_typing(self, create_bot):
        """Tests the cache typing raises on incorrect instances"""
        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, Library.DPY, cache=MockClass())

        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, Library.DPY, cache=MockClass)

        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, Library.DPY, cache=1)

    def test_add_ignored_item(self, create_handler):
        """Tests the handler adds ignored items correctly"""
        # ensure they start empty
        assert create_handler.options == Options(use_timeouts=False)

    # TODO Cannot test this until files get stubbed
    """
    def test_init_bot_raises(self, create_bot):
        with pytest.raises(ValueError):
            AntiSpamHandler(1)

        with pytest.raises(ValueError):
            AntiSpamHandler("1")

        with pytest.raises(ValueError):
            AntiSpamHandler(AntiSpamHandler(create_bot))

        with pytest.raises(ValueError):
            AntiSpamHandler(MockClass)
    """

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
        assert create_handler.cache.cache.get(1).options == Options(use_timeouts=False)

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
            await create_handler.add_guild_log_channel("one", 1)

        with pytest.raises(ValueError):
            await create_handler.add_guild_log_channel({"one": 1}, 1)

    @pytest.mark.asyncio
    async def test_add_guild_log_channel(self):
        # Mock it up
        mock_channel = MagicMock()
        mock_channel.id = 2
        mock_channel.guild.id = 1

        mock_bot = MagicMock()
        mock_bot.fetch_channel = AsyncMock(return_value=mock_channel)

        assert await mock_bot.fetch_channel.called_with(1)

        handler = AntiSpamHandler(mock_bot, Library.DPY)

        await handler.add_guild_log_channel(2, 1)
        g = await handler.cache.get_guild(1)
        assert g.log_channel_id == 2

    @pytest.mark.asyncio
    async def test_add_guild_log_channel_exists(self):
        mock_channel = MagicMock()
        mock_channel.id = 2
        mock_channel.guild.id = 1

        mock_bot = MagicMock()
        mock_bot.fetch_channel = AsyncMock(return_value=mock_channel)

        assert await mock_bot.fetch_channel.called_with(1)

        handler = AntiSpamHandler(mock_bot, Library.DPY)
        await handler.cache.set_guild(Guild(1, Options()))

        await handler.add_guild_log_channel(2, 1)
        g = await handler.cache.get_guild(1)
        assert g.log_channel_id == 2

    @pytest.mark.asyncio
    async def test_remove_guild_log_channel(self, create_handler: AntiSpamHandler):
        await create_handler.remove_guild_log_channel(1)  # shouldnt raise

        await create_handler.cache.set_guild(Guild(1, Options(), log_channel_id=1))
        result = await create_handler.cache.get_guild(1)
        assert result.log_channel_id == 1

        await create_handler.remove_guild_log_channel(1)
        result = await create_handler.cache.get_guild(1)
        assert result.log_channel_id is None

    @pytest.mark.asyncio
    async def test_load_from_dict(self, create_bot):
        test_data = {
            "cache": "MemoryCache",
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

        await AntiSpamHandler.load_from_dict(create_bot, test_data, Library.DPY)

    @pytest.mark.asyncio
    async def test_load_from_dict_fails(self, create_bot):
        test_data = {
            "cache": "MemoryCache",
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
            MagicMock(side_effect=discord.HTTPException), test_data, Library.DPY
        )

        await AntiSpamHandler.load_from_dict(
            create_bot, 1, Library.DPY, raise_on_exception=False
        )

        with pytest.raises(TypeError):
            await AntiSpamHandler.load_from_dict(create_bot, 1, Library.DPY)

    @pytest.mark.asyncio
    async def test_save_to_dict(self, create_handler: AntiSpamHandler, get_test_path):
        await create_handler.save_to_dict()

        await create_handler.cache.set_guild(Guild(1, Options()))
        data = await create_handler.save_to_dict()
        with open(os.path.join(get_test_path, "raw.json"), "r") as file:
            stored_data = json.load(file)

        assert data == stored_data

    @pytest.mark.asyncio
    async def test_save_to_dict_with_plugin(
        self, create_handler: AntiSpamHandler, get_test_path
    ):
        await create_handler.cache.set_guild(Guild(1, Options()))

        class Plugin(BasePlugin):
            async def save_to_dict(self):
                return {"Plugin me"}

        create_handler.register_plugin(Plugin())
        data = await create_handler.save_to_dict()

        with open(os.path.join(get_test_path, "raw.json"), "r") as file:
            stored_data = json.load(file)
        stored_data["pre_invoke_plugins"]["Plugin"] = {"Plugin me"}

        assert data == stored_data

        create_handler.unregister_plugin("Plugin")
        create_handler.register_plugin(Plugin(is_pre_invoke=False))
        stored_data["pre_invoke_plugins"] = {}
        stored_data["after_invoke_plugins"]["Plugin"] = {"Plugin me"}

        data_two = await create_handler.save_to_dict()
        assert data_two == stored_data

    @pytest.mark.asyncio
    async def test_load_from_dict_with_plugin(self, create_bot, get_test_path):
        class Plugin(BasePlugin):
            @classmethod
            async def load_from_dict(cls, ash, data):
                ref = cls()
                ref.test = data
                return ref

        with open(os.path.join(get_test_path, "raw.json"), "r") as file:
            stored_data = json.load(file)

        stored_data["pre_invoke_plugins"]["Plugin"] = {"Plugin me"}
        # stored_data["after_invoke_plugins"]["Plugin"] = {"Plugin me"}

        ash = await AntiSpamHandler.load_from_dict(
            create_bot, stored_data, Library.DPY, plugins={Plugin}
        )

        assert len(ash.pre_invoke_plugins) == 1
        # assert len(ash.after_invoke_plugins) == 1

        assert ash.pre_invoke_plugins["plugin"].is_pre_invoke is True
        # assert ash.after_invoke_plugins["plugin"].is_pre_invoke is False

        assert ash.pre_invoke_plugins["plugin"].test == {"Plugin me"}

    def test_register_extension(self, create_handler: AntiSpamHandler):
        with pytest.raises(PluginError):
            create_handler.register_plugin(MockClass())

        class Test(BasePlugin):
            def __init__(self, invoke=True):
                self.is_pre_invoke = invoke

        assert len(create_handler.pre_invoke_plugins.values()) == 0
        create_handler.register_plugin(Test())
        assert len(create_handler.pre_invoke_plugins.values()) == 1

        # Test overwrite
        with pytest.raises(PluginError):
            create_handler.register_plugin(Test())

        create_handler.register_plugin(Test(), force_overwrite=True)

        assert len(create_handler.after_invoke_plugins.values()) == 0
        create_handler.register_plugin(Test(invoke=False), force_overwrite=True)
        assert len(create_handler.after_invoke_plugins.values()) == 1

    def test_unregister_extension(self, create_handler: AntiSpamHandler):
        class Test(BasePlugin):
            def __init__(self, invoke=True):
                self.is_pre_invoke = invoke

        create_handler.register_plugin(Test(invoke=False))
        assert len(create_handler.after_invoke_plugins.values()) == 1
        create_handler.unregister_plugin("Test")
        assert len(create_handler.after_invoke_plugins.values()) == 0

        with pytest.raises(PluginError):
            create_handler.unregister_plugin("Invalid Extension")

        create_handler.register_plugin(Test())
        assert len(create_handler.pre_invoke_plugins.values()) == 1
        create_handler.unregister_plugin("Test")
        assert len(create_handler.pre_invoke_plugins.values()) == 0

    @pytest.mark.asyncio()
    async def test_propagate_exits(self):
        bot = AsyncMock()
        bot.user.id = 9
        create_handler = AntiSpamHandler(bot, Library.DPY)

        # TODO Until files get stubbed, we cant check this.
        """
        with pytest.raises(ValueError):
            await create_handler.propagate(1)

        with pytest.raises(ValueError):
            await create_handler.propagate("2")

        with pytest.raises(ValueError):
            await create_handler.propagate(MockClass)
        """

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

    @pytest.mark.asyncio
    async def test_propagate_guild_ignore(self):
        bot = AsyncMock()
        bot.user.id = 919191
        create_handler = AntiSpamHandler(bot, Library.DPY)

        create_handler.options.ignored_guilds.add(1)

        message = MockedMessage(guild_id=1).to_mock()
        return_data = await create_handler.propagate(message)

        assert return_data["status"] == "Ignoring this guild: 1"

    @pytest.mark.asyncio
    async def test_propagate_role_ignores(self):
        bot = AsyncMock()
        bot.user.id = 919191
        create_handler = AntiSpamHandler(bot, Library.DPY)

        create_handler.options.ignored_roles.add(252525)

        message = MockedMessage().to_mock()
        return_data = await create_handler.propagate(message)
        assert return_data["status"] == "Ignoring this role: 252525"

    @pytest.mark.asyncio
    async def test_propagate_missing_perms(self):
        bot = AsyncMock()
        bot.user.id = 919191
        create_handler = AntiSpamHandler(bot, Library.DPY)

        message = MockedMessage().to_mock()
        message.guild.me.guild_permissions.kick_members = False
        message.guild.me.guild_permissions.ban_members = False

        with pytest.raises(MissingGuildPermissions):
            await create_handler.propagate(message)

        # Reset cache rather then make a new test
        create_handler.cache.cache = {}

        message.guild.me.guild_permissions.kick_members = True
        message.guild.me.guild_permissions.ban_members = False

        with pytest.raises(MissingGuildPermissions):
            await create_handler.propagate(message)

    @pytest.mark.asyncio
    async def test_propagate_pre_invoke(self):
        bot = AsyncMock()
        bot.user.id = 919191
        create_handler = AntiSpamHandler(bot, Library.DPY)

        class PreInvoke(BasePlugin):
            async def propagate(self, msg):
                return 1

        create_handler.register_plugin(PreInvoke())

        message = MockedMessage().to_mock()
        return_data = await create_handler.propagate(message)

        assert len(return_data.pre_invoke_extensions) == 1
        assert return_data.pre_invoke_extensions["PreInvoke"] == 1

    @pytest.mark.asyncio
    async def test_propagate_after_invoke(self):
        bot = AsyncMock()
        bot.user.id = 919191
        create_handler = AntiSpamHandler(bot, Library.DPY)

        class AfterInvoke(BasePlugin):
            def __init__(self):
                super().__init__(False)

            async def propagate(self, msg, data):
                return 2

        create_handler.register_plugin(AfterInvoke())

        message = MockedMessage().to_mock()
        return_data = await create_handler.propagate(message)

        assert len(return_data.after_invoke_extensions) == 1
        assert return_data.after_invoke_extensions["AfterInvoke"] == 2

    @pytest.mark.asyncio
    async def test_propagate_role_raises(self):
        bot = AsyncMock()
        bot.user.id = 919191
        create_handler = AntiSpamHandler(bot, Library.DPY)

        create_handler.options.ignored_roles.add(252525)

        message = MockedMessage().to_mock()
        return_data = await create_handler.propagate(message)
        assert return_data["status"] == "Ignoring this role: 252525"

    @pytest.mark.asyncio
    async def test_propagate_stats_hook(self, create_handler):
        """Tests the stats cancel_next_invocation hook works"""

        class MockPlugin(BasePlugin):
            async def propagate(
                self, message, data: Optional[CorePayload] = None
            ) -> dict:
                return {"cancel_next_invocation": True}

        bot_mock = AsyncMock()
        bot_mock.bot.user.id = 1500
        create_handler.bot = bot_mock

        stats_plugin = StatsPlugin(create_handler)

        create_handler.register_plugin(MockPlugin())
        create_handler.register_plugin(stats_plugin)

        with pytest.raises(InvocationCancelled):
            await create_handler.propagate(MockedMessage().to_mock())

        stats_plugin.data = {"pre_invoke_calls": {"MockPlugin": {}}}

        with pytest.raises(InvocationCancelled):
            await create_handler.propagate(MockedMessage().to_mock())

        create_handler.unregister_plugin("Stats")

        class Stats(BasePlugin):
            def __init__(self):
                super().__init__(False)

            async def propagate(
                self, message, data: Optional[CorePayload] = None
            ) -> dict:
                return {"cancel_next_invocation": True}

        create_handler.register_plugin(Stats())

        with pytest.raises(InvocationCancelled):
            # Should skip tryna set stats stuff
            await create_handler.propagate(MockedMessage().to_mock())

    @pytest.mark.asyncio
    async def test_propagate_cancel_next_invoke(self, create_handler):
        class MockPlugin(BasePlugin):
            async def propagate(
                self, message, data: Optional[CorePayload] = None
            ) -> dict:
                return {"cancel_next_invocation": True}

        bot_mock = AsyncMock()
        bot_mock.bot.user.id = 1500
        create_handler.bot = bot_mock

        create_handler.register_plugin(MockPlugin())

        with pytest.raises(InvocationCancelled):
            await create_handler.propagate(MockedMessage().to_mock())

        class MockPluginTwo(BasePlugin):
            async def propagate(
                self, message, data: Optional[CorePayload] = None
            ) -> dict:
                return {}

        create_handler.unregister_plugin("MockPlugin")
        create_handler.register_plugin(MockPluginTwo())
        await create_handler.propagate(MockedMessage().to_mock())

    def test_hikari_setup(self):
        handler = AntiSpamHandler(
            commands.Bot(command_prefix="!"), library=Library.HIKARI
        )
        assert handler.lib_handler.__class__.__name__ == "Hikari"

    def test_dpy_setup(self):
        handler = AntiSpamHandler(commands.Bot(command_prefix="!"), Library.DPY)
        assert handler.lib_handler.__class__.__name__ == "DPY"

    @pytest.mark.asyncio
    async def test_clean_cache_basic(self, create_handler):
        """Tests the basics of clean cache without strict mode or messages"""
        assert not bool(create_handler.cache.cache)

        await create_handler.cache.set_member(Member(1, 2))
        assert bool(create_handler.cache.cache)

        await create_handler.clean_cache()
        assert not bool(create_handler.cache.cache)

        await create_handler.cache.set_guild(Guild(1, options=create_handler.options))
        assert bool(create_handler.cache.cache)

        await create_handler.clean_cache()
        assert not bool(create_handler.cache.cache)

    @pytest.mark.asyncio
    async def test_clean_cache_member_warn_count(self, create_handler):
        await create_handler.cache.set_member(Member(1, 2, warn_count=2))
        assert bool(create_handler.cache.cache)

        await create_handler.clean_cache()
        assert bool(create_handler.cache.cache)

    @pytest.mark.asyncio
    async def test_clean_cache_strict_member(self, create_handler):
        """Tests clean_cache on members with strict mode"""

        await create_handler.cache.set_member(Member(1, 1))
        assert bool(create_handler.cache.cache)

        await create_handler.clean_cache(strict=True)
        assert not bool(create_handler.cache.cache)

        await create_handler.cache.set_member(
            Member(1, 1, messages=[Message(1, 2, 3, 4, "Hello")])
        )
        assert bool(create_handler.cache.cache)

        await create_handler.clean_cache(strict=True)
        assert bool(create_handler.cache.cache)

    @pytest.mark.asyncio
    async def test_clean_cache_strict_guild(self, create_handler):
        """Tests clean_cache on guilds with strict mode"""
        await create_handler.cache.set_guild(Guild(1, options=create_handler.options))
        assert bool(create_handler.cache.cache)

        await create_handler.clean_cache(strict=True)
        assert not bool(create_handler.cache.cache)

        await create_handler.cache.set_guild(Guild(1, Options(no_punish=True)))
        assert bool(create_handler.cache.cache)

        await create_handler.clean_cache(strict=True)
        assert bool(create_handler.cache.cache)

    @pytest.mark.asyncio
    async def test_plugin_blacklists(self, create_handler):
        """Tests blacklisted guilds get skipped within plugin calls"""

        class Test(BasePlugin):
            def __init__(self, invoke=True):
                super().__init__(invoke)

        test = Test()
        test.blacklisted_guilds.add(13123)
        test.propagate = AsyncMock(return_value={})
        create_handler.register_plugin(test)

        assert test.propagate.call_count == 0

        await create_handler.propagate(MockedMessage().to_mock())
        await create_handler.propagate(MockedMessage(guild_id=13123).to_mock())

        assert test.propagate.call_count == 1
        create_handler.unregister_plugin("test")

        test = Test(False)
        test.blacklisted_guilds.add(13123)
        test.propagate = AsyncMock(return_value={})
        create_handler.register_plugin(test)

        assert test.propagate.call_count == 0

        await create_handler.propagate(MockedMessage().to_mock())
        await create_handler.propagate(MockedMessage(guild_id=13123).to_mock())

        assert test.propagate.call_count == 1

    @pytest.mark.asyncio
    async def test_invalid_message(self, create_handler):
        """Tests InvalidMessage gets raised right"""
        message = MockedMessage().to_mock()
        message.content = None
        message.embeds = None
        message.attachments = True

        return_data = await create_handler.propagate(message)
        assert return_data == {"status": "We don't check against attachments"}

    def test_set_cache(self, create_handler):
        """Tests set_cache works as expected"""
        assert isinstance(create_handler.cache, MemoryCache)

        with pytest.raises(ValueError):
            create_handler.set_cache(1)

        create_handler.set_cache(MongoCache(create_handler, "Mock"))
        assert isinstance(create_handler.cache, MongoCache)

    @pytest.mark.asyncio
    async def test_conflicting_init_args(self, create_bot):
        options = Options(
            no_punish=True,
            delete_spam=True,
            warn_only=True,
            per_channel_spam=True,
            use_timeouts=False,
        )
        AntiSpamHandler(create_bot, Library.DPY, options=options)

    @pytest.mark.asyncio
    async def test_custom_lib(self, create_bot):
        ash = AntiSpamHandler(create_bot, library=Library.CUSTOM)
        with pytest.raises(UnsupportedAction):
            await ash.propagate(MockedMessage().to_mock())

    @pytest.mark.asyncio
    async def test_get_options(self, create_handler):
        options = await create_handler.get_options()
        assert options == create_handler.options
        assert id(options) != id(create_handler.options)

    @pytest.mark.asyncio
    async def test_save_to_dict_not_implemented(self, create_handler):
        """Tests Plugins without save methods work properly"""

        class Plugin(BasePlugin):
            pass

        create_handler.register_plugin(Plugin())

        r_1 = await create_handler.save_to_dict()
        assert r_1["pre_invoke_plugins"] == dict()
        assert r_1["after_invoke_plugins"] == dict()

        create_handler.unregister_plugin("Plugin")

        create_handler.register_plugin(Plugin(is_pre_invoke=False))
        r_2 = await create_handler.save_to_dict()
        assert r_2["pre_invoke_plugins"] == dict()
        assert r_2["after_invoke_plugins"] == dict()

    @pytest.mark.asyncio
    async def test_visualizer(self, create_handler):
        msg = await create_handler.visualize(
            "$MEMBERID", MockedMessage(author_id=1).to_mock()
        )
        assert msg == "1"

        embed = await create_handler.visualize(
            '{"title": "$MEMBERID"}', MockedMessage(author_id=1).to_mock()
        )
        assert isinstance(embed, nextcord.Embed)
        assert embed.title == nextcord.Embed(title="1").title

    @pytest.mark.asyncio
    async def test_load_from_dict_plugins_pre_invoke(self, create_bot, get_test_path):
        """Tests load_from_dict edge cases"""

        class Plugin(BasePlugin):
            @classmethod
            async def load_from_dict(cls, ash, data):
                ref = cls()
                ref.test = data
                return ref

        with open(os.path.join(get_test_path, "raw.json"), "r") as file:
            stored_data = json.load(file)

        stored_data["pre_invoke_plugins"]["Plugin"] = {"Plugin me"}

        # This skips the plugin due to the missing lookup
        ash = await AntiSpamHandler.load_from_dict(create_bot, stored_data, Library.DPY)

        assert len(ash.pre_invoke_plugins) == 0

    @pytest.mark.asyncio
    async def test_load_from_dict_plugins_after_invoke(self, create_bot, get_test_path):
        """Tests load_from_dict edge cases"""

        class Plugin(BasePlugin):
            def __init__(self):
                super().__init__(is_pre_invoke=False)

            @classmethod
            async def load_from_dict(cls, ash, data):
                ref = cls()
                ref.test = data
                return ref

        with open(os.path.join(get_test_path, "raw.json"), "r") as file:
            stored_data = json.load(file)

        stored_data["after_invoke_plugins"]["Plugin"] = {"Plugin me"}

        # This skips the plugin due to the missing lookup
        ash = await AntiSpamHandler.load_from_dict(create_bot, stored_data, Library.DPY)
        assert len(ash.after_invoke_plugins) == 0

        ash_2 = await AntiSpamHandler.load_from_dict(
            create_bot, stored_data, Library.DPY, plugins={Plugin}
        )
        assert len(ash_2.after_invoke_plugins) == 1

    def test_library_inits(self, create_bot):
        hikari = AntiSpamHandler(create_bot, library=Library.HIKARI)
        assert isinstance(hikari.lib_handler, Hikari)

        disnake = AntiSpamHandler(create_bot, library=Library.DISNAKE)
        assert isinstance(disnake.lib_handler, Disnake)

        enhanced_dpy = AntiSpamHandler(create_bot, library=Library.ENHANCED_DPY)
        assert isinstance(enhanced_dpy.lib_handler, EnhancedDPY)

        nextcord = AntiSpamHandler(create_bot, library=Library.NEXTCORD)
        assert isinstance(nextcord.lib_handler, Nextcord)

        with pytest.raises(UnsupportedAction):
            AntiSpamHandler(create_bot, library=Library.PYCORD)

        dpy = AntiSpamHandler(create_bot, library=Library.DPY)
        assert isinstance(dpy.lib_handler, DPY)

    @pytest.mark.asyncio
    async def test_clean_cache_with_custom_options(self, create_handler):
        await create_handler.cache.set_guild(
            Guild(1, options=Options(ignore_bots=False))
        )

        r_1 = await create_handler.cache.get_guild(1)
        assert r_1.options.ignore_bots is False

        await create_handler.clean_cache()

        r_2 = await create_handler.cache.get_guild(1)
        assert id(r_1) != id(r_2)
        assert r_2.options.ignore_bots is False
