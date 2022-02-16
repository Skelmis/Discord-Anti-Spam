import datetime
from unittest.mock import AsyncMock

import hikari
import pytest

from antispam import LogicError, MissingGuildPermissions, Options
from antispam.dataclasses import CorePayload, Guild, Member, Message
from antispam.libs.lib_hikari import Hikari

from .fixtures import (
    MockClass,
    create_bot,
    create_dpy_lib_handler,
    create_handler,
    create_memory_cache,
)
from .mocks import MockedMessage


# noinspection DuplicatedCode
class TestLibHikari:
    """A class devoted to testing hikari.py"""

    def test_init(self, create_handler):
        Hikari(create_handler)
