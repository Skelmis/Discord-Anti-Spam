import datetime
from unittest.mock import AsyncMock

import discord
import pytest

from antispam.dataclasses import Guild, Member, CorePayload, Message

from antispam import Options, LogicError, MissingGuildPermissions
from antispam.libs.hikari import Hikari
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
class TestLibHikari:
    """A class devoted to testing hikari.py"""

    def test_init(self, create_handler):
        Hikari(create_handler)
