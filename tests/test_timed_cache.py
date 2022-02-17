import asyncio
from datetime import timedelta

import pytest

from antispam import ExistingEntry, NonExistentEntry


class TestTimedCache:
    def test_cache_add(self, create_timed_cache):
        assert not create_timed_cache.cache

        create_timed_cache.add_entry("key", "value")
        assert create_timed_cache.cache

        with pytest.raises(ExistingEntry):
            create_timed_cache.add_entry("key", "different value")

        create_timed_cache.add_entry("key", "A third value", override=True)

    def test_delete_entry(self, create_timed_cache):
        create_timed_cache.add_entry("key", "value")
        assert "key" in create_timed_cache.cache

        create_timed_cache.delete_entry("key")
        assert "key" not in create_timed_cache.cache

        # Idempotent
        create_timed_cache.delete_entry("key")

    def test_get_entry(self, create_timed_cache):
        create_timed_cache.add_entry("key", "value")
        assert "key" in create_timed_cache.cache

        r_1 = create_timed_cache.get_entry("key")
        assert r_1 == "value"

        with pytest.raises(NonExistentEntry):
            create_timed_cache.get_entry("key_2")

    def test_contains(self, create_timed_cache):
        assert "key" not in create_timed_cache

        create_timed_cache.add_entry("key", "value")

        assert "key" in create_timed_cache

    @pytest.mark.asyncio
    async def test_eviction(self, create_timed_cache):
        create_timed_cache.add_entry("key", "value", ttl=timedelta(seconds=1))
        assert "key" in create_timed_cache
        assert create_timed_cache.cache
        await asyncio.sleep(1.25)
        assert "key" not in create_timed_cache
        assert not create_timed_cache.cache

    @pytest.mark.asyncio
    async def test_force_clean(self, create_timed_cache):
        create_timed_cache.add_entry("key", "value", ttl=timedelta(seconds=1))
        create_timed_cache.add_entry(
            "key_2",
            "value",
        )
        assert "key" in create_timed_cache
        assert "key_2" in create_timed_cache

        await asyncio.sleep(1.25)

        create_timed_cache.force_clean()
        assert "key" not in create_timed_cache
        assert "key_2" in create_timed_cache
