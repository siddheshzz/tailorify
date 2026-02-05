"""RedisCache unit tests — mocked redis client, no network."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.core.cache import RedisCache, build_cache_key, cache_key, invalidate_cache


# ---------------------------------------------------------------------------
# Disconnected state — every operation is a no-op
# ---------------------------------------------------------------------------
class TestRedisCacheDisconnected:
    @pytest.fixture
    def rc(self):
        return RedisCache()  # _connected defaults to False

    async def test_get_returns_none(self, rc):
        assert await rc.get("k") is None

    async def test_set_returns_false(self, rc):
        assert await rc.set("k", {"x": 1}) is False

    async def test_delete_returns_false(self, rc):
        assert await rc.delete("k") is False

    async def test_delete_pattern_returns_zero(self, rc):
        assert await rc.delete_pattern("prefix:*") == 0

    async def test_exists_returns_false(self, rc):
        assert await rc.exists("k") is False

    async def test_increment_returns_zero(self, rc):
        assert await rc.increment("counter") == 0


# ---------------------------------------------------------------------------
# Connected state — redis_client is an AsyncMock
# ---------------------------------------------------------------------------
class TestRedisCacheConnected:
    @pytest.fixture
    def rc(self):
        cache = RedisCache()
        cache._connected = True
        cache.redis_client = AsyncMock()
        return cache

    # -- get --
    async def test_get_deserializes_json_on_hit(self, rc):
        rc.redis_client.get.return_value = '{"name": "test"}'
        assert await rc.get("user:1") == {"name": "test"}
        rc.redis_client.get.assert_awaited_once_with("user:1")

    async def test_get_returns_none_on_miss(self, rc):
        rc.redis_client.get.return_value = None
        assert await rc.get("miss") is None

    async def test_get_returns_none_on_redis_error(self, rc):
        rc.redis_client.get.side_effect = Exception("boom")
        assert await rc.get("err") is None  # no crash

    # -- set --
    async def test_set_serializes_and_calls_setex(self, rc):
        result = await rc.set("k", [1, 2], ttl=120)
        assert result is True
        rc.redis_client.setex.assert_awaited_once_with(
            "k", 120, json.dumps([1, 2], default=str)
        )

    async def test_set_uses_default_ttl_when_none(self, rc):
        from app.core.config import settings

        await rc.set("k", "val")
        _, ttl_arg, _ = rc.redis_client.setex.await_args[0]
        assert ttl_arg == settings.CACHE_DEFAULT_TTL

    async def test_set_returns_false_on_redis_error(self, rc):
        rc.redis_client.setex.side_effect = Exception("oops")
        assert await rc.set("k", "v") is False

    # -- delete --
    async def test_delete_calls_redis_delete(self, rc):
        assert await rc.delete("old") is True
        rc.redis_client.delete.assert_awaited_once_with("old")

    async def test_delete_returns_false_on_error(self, rc):
        rc.redis_client.delete.side_effect = Exception("err")
        assert await rc.delete("k") is False

    # -- exists --
    async def test_exists_true_when_key_present(self, rc):
        rc.redis_client.exists.return_value = 1
        assert await rc.exists("k") is True

    async def test_exists_false_when_key_missing(self, rc):
        rc.redis_client.exists.return_value = 0
        assert await rc.exists("k") is False

    # -- increment --
    async def test_increment_returns_new_value(self, rc):
        rc.redis_client.incrby.return_value = 7
        assert await rc.increment("counter", 3) == 7
        rc.redis_client.incrby.assert_awaited_once_with("counter", 3)

    # -- connect --
    async def test_connect_skips_when_caching_disabled(self):
        rc = RedisCache()
        with patch("app.core.cache.settings") as mock_settings:
            mock_settings.ENABLE_CACHING = False
            await rc.connect()
        assert rc._connected is False


# ---------------------------------------------------------------------------
# Pure helper functions
# ---------------------------------------------------------------------------
class TestCacheKeyHelpers:
    def test_cache_key_positional_args(self):
        assert cache_key("orders", "123") == "orders:123"

    def test_cache_key_kwargs_sorted_alphabetically(self):
        assert cache_key(status="active", user="bob") == "status:active:user:bob"

    def test_cache_key_skips_none_positional(self):
        assert cache_key("a", None, "b") == "a:b"

    def test_cache_key_skips_none_kwargs(self):
        assert cache_key(a="1", b=None) == "a:1"

    def test_build_cache_key_prefix_only(self):
        assert build_cache_key("users") == "users"

    def test_build_cache_key_with_kwargs(self):
        key = build_cache_key("orders", user_id="abc", status="pending")
        assert key.startswith("orders:")
        assert "status:pending" in key
        assert "user_id:abc" in key

    def test_build_cache_key_filters_none(self):
        key = build_cache_key("x", a="1", b=None)
        assert "b:" not in key

    def test_build_cache_key_filters_session_like_objects(self):
        """Anything with an `execute` attr (DB session) is excluded."""

        class FakeSession:
            async def execute(self):
                pass

        key = build_cache_key("x", db=FakeSession(), id="99")
        assert "db:" not in key
        assert "id:99" in key


# ---------------------------------------------------------------------------
# invalidate_cache — integration with the module-level `cache` singleton
# ---------------------------------------------------------------------------
class TestInvalidateCache:
    async def test_with_kwargs_deletes_specific_key(self):
        from app.core import cache as cache_module

        mock_cache = AsyncMock()
        original = cache_module.cache
        cache_module.cache = mock_cache
        try:
            await invalidate_cache("orders", user_id="123")
            mock_cache.delete.assert_awaited_once()
            deleted_key = mock_cache.delete.await_args[0][0]
            assert deleted_key.startswith("orders:")
            assert "user_id:123" in deleted_key
        finally:
            cache_module.cache = original

    async def test_without_kwargs_deletes_pattern(self):
        from app.core import cache as cache_module

        mock_cache = AsyncMock()
        original = cache_module.cache
        cache_module.cache = mock_cache
        try:
            await invalidate_cache("products")
            mock_cache.delete_pattern.assert_awaited_once_with("products:*")
        finally:
            cache_module.cache = original
