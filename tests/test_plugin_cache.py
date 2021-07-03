import pytest

from discord.ext import commands

# noinspection PyUnresolvedReferences
from discord.ext.antispam import (
    PluginCache,
    GuildNotFound,
    MemberNotFound,
    MemberAddonNotFound,
    GuildAddonNotFound,
    Options,
    AntiSpamHandler,
)

from discord.ext.antispam.dataclasses import Member, Guild  # noqa

from hypothesis import given
from hypothesis.strategies import text, dictionaries, floats, lists, datetimes

from .fixtures import create_bot, create_handler, create_plugin_cache, MockClass


# noinspection DuplicatedCode
class TestPluginCache:
    def test_init_key(self, create_plugin_cache):
        """Test the cache extracts the caller's name for a key"""
        assert create_plugin_cache.key == "MockClass"

    # MEMBER GET
    @pytest.mark.asyncio
    async def test_get_member_data_fails_on_guild(
        self, create_plugin_cache: PluginCache
    ):
        """Test the cache raises GuildNotFound"""
        with pytest.raises(GuildNotFound):
            await create_plugin_cache.get_member_data(1, 1)

    @pytest.mark.asyncio
    async def test_get_member_data_fails_on_member(
        self, create_plugin_cache: PluginCache
    ):
        """Test the cache raises MemberNotFound"""
        await create_plugin_cache.set_guild_data(1, [])

        with pytest.raises(MemberNotFound):
            await create_plugin_cache.get_member_data(1, 1)

    @pytest.mark.asyncio
    async def test_get_member_data_fails_on_member_addon(
        self, create_plugin_cache: PluginCache, create_handler
    ):
        """Test the cache raises MemberNotFound"""
        await create_handler.cache.set_member(Member(1, 1))

        with pytest.raises(MemberAddonNotFound):
            await create_plugin_cache.get_member_data(1, 1)

    # MEMBER SET
    @pytest.mark.asyncio
    @given(arg=text())
    async def test_set_member_data_text(self, arg):
        """Test the cache sets member addon's correct using text"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, arg)

        assert await plugin_cache.get_member_data(1, 1) == arg

    @pytest.mark.asyncio
    @given(arg=dictionaries(text(), floats()))
    async def test_set_member_data_dictionaries(self, arg):
        """Test the cache sets member addon's correct using dictionaries"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, arg)

        assert await plugin_cache.get_member_data(1, 1) == arg

    @pytest.mark.asyncio
    @given(arg=lists(datetimes()))
    async def test_set_member_data_dictionaries(self, arg):
        """Test the cache sets member addon's correct using lists of datetimes"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_member_data(1, 1)

        await plugin_cache.set_member_data(1, 1, arg)

        assert await plugin_cache.get_member_data(1, 1) == arg

    @pytest.mark.asyncio
    async def test_set_member_data_key_error(self, create_plugin_cache):
        """Tests an edge case on a KeyError guild setting"""
        await create_plugin_cache.handler.cache.set_guild(Guild(1, Options()))

        await create_plugin_cache.set_member_data(1, 1, 2)

        assert await create_plugin_cache.get_member_data(1, 1) == 2

    # GUILD GET
    @pytest.mark.asyncio
    async def test_get_guild_data_fails(self, create_plugin_cache: PluginCache):
        """Test the cache raises GuildNotFound"""
        with pytest.raises(GuildNotFound):
            await create_plugin_cache.get_guild_data(1)

    @pytest.mark.asyncio
    async def test_get_guild_data_fails_on_guild_addon(
        self, create_plugin_cache: PluginCache, create_handler
    ):
        """Test the cache raises GuildAddonNotFound"""
        await create_handler.cache.set_guild(Guild(1, Options()))

        with pytest.raises(GuildAddonNotFound):
            await create_plugin_cache.get_guild_data(1)

    # GUILD SET
    @pytest.mark.asyncio
    @given(arg=text())
    async def test_set_guild_data_text(self, arg):
        """Test the cache sets guild addon's correct using text"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_guild_data(1)

        await plugin_cache.set_guild_data(1, arg)

        assert await plugin_cache.get_guild_data(1) == arg

    @pytest.mark.asyncio
    @given(arg=dictionaries(text(), floats()))
    async def test_set_guild_data_dictionaries(self, arg):
        """Test the cache sets guild addon's correct using dictionaries"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_guild_data(1)

        await plugin_cache.set_guild_data(1, arg)

        assert await plugin_cache.get_guild_data(1) == arg

    @pytest.mark.asyncio
    @given(arg=lists(datetimes()))
    async def test_set_guild_data_dictionaries(self, arg):
        """Test the cache sets guild addon's correct using lists of datetimes"""
        plugin_cache = PluginCache(AntiSpamHandler(commands.Bot("!")), MockClass())

        with pytest.raises(GuildNotFound):
            await plugin_cache.get_guild_data(1)

        await plugin_cache.set_guild_data(1, arg)

        assert await plugin_cache.get_guild_data(1) == arg
