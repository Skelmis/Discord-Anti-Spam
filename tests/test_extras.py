import pytest

from antispam.base_plugin import BasePlugin
from antispam.enums.state import ASHEnum
from tests.mocks import MockedMessage

"""Some simple tests which don't need a whole file"""


def test_base_init():
    b = BasePlugin()
    assert type(b) == BasePlugin


@pytest.mark.asyncio
async def test_base_prop():
    b = BasePlugin()
    with pytest.raises(NotImplementedError):
        await b.propagate(MockedMessage().to_mock())


def test_state_enum():
    assert ASHEnum.BAN.value == 0
    assert ASHEnum.KICK.value == 1
    assert ASHEnum.WARN_COUNTER.value == 2
    assert ASHEnum.KICK_COUNTER.value == 3
