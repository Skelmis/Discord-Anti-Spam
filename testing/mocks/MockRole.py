"""
This 'mocks' a discord.Role so we can use it for testing
"""
from unittest.mock import AsyncMock


def get_mocked_role(*, name=None, id=None):
    """
    Return a mocked, usable role object
    """
    name = name or "Mocked Role"
    id = int(id) if id else 151515

    mock = AsyncMock(name="Role Mock")
    mock.id = id
    mock.name = name
    mock.mention = f"<@&{id}>"

    return mock
