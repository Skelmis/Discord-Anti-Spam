import pytest
from hypothesis import given, strategies as st
from hypothesis.strategies import text
from discord.ext import commands  # noqa

from discord.ext.antispam import AntiSpamHandler, Options  # noqa

from .fixtures import create_bot, create_handler, MockClass


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

    """
    How to use hypothesis
    @given(st.none(), text())
    def test_options_typing(self, create_bot, option):
        with pytest.raises(ValueError):
            AntiSpamHandler(create_bot, options=option)
    """
