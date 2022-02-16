import pytest
from discord.ext import commands
from hypothesis import given
from hypothesis.strategies import datetimes, dictionaries, floats, lists, text

# noinspection PyUnresolvedReferences
from antispam import (
    AntiSpamHandler,
    GuildAddonNotFound,
    GuildNotFound,
    MemberAddonNotFound,
    MemberNotFound,
    Options,
    PluginCache,
)
from antispam.dataclasses import Guild, Member  # noqa

from .fixtures import MockClass, create_bot, create_handler, create_plugin_cache

"""A test file devoted to hypothesis.
These tests do not run on ci due to time
constraints however they are used for
better test argument coverage
"""


class TestHypoth:
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
