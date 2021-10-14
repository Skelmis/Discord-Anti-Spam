import pytest

from antispam.base_plugin import BasePlugin
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
