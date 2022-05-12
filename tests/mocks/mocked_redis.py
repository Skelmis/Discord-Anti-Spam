from typing import Dict, Optional


class MockedRedis:
    """A mock aioredis.Redis class that
    imitates the required methods.
    """

    def __init__(self):
        self._data: Dict[str, dict] = {}

    @property
    def cache(self) -> Dict:
        return self._data

    async def get(self, key) -> Optional[dict]:
        try:
            return self._data[key]
        except:
            return None

    async def set(self, key, value):
        self._data[key] = value

    async def delete(self, key):
        try:
            self._data.pop(key)
        except:
            pass

    async def flushdb(self, *args, **kwargs):
        self._data = {}

    async def keys(self, pattern: str):
        if pattern.startswith("GUILD"):
            return self._get_guilds()

        member, guild_id, wildcard = pattern.split(":")
        return self._get_members(guild_id)

    def _get_guilds(self):
        return [
            key.encode("utf-8") for key in self._data.keys() if key.startswith("GUILD")
        ]

    def _get_members(self, guild_id):
        return [
            key.encode("utf-8")
            for key in self._data.keys()
            if key.startswith(f"MEMBER:{guild_id}")
        ]
