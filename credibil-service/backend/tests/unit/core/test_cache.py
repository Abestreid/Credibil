from __future__ import annotations

from credibil.core.cache import _make_cache_key


class TestCacheHelpers:
    def test_make_cache_key_deterministic(self):
        k1 = _make_cache_key("test", "arg1", "arg2", key="value")
        k2 = _make_cache_key("test", "arg1", "arg2", key="value")
        assert k1 == k2
        assert k1.startswith("credibil:test:")

    def test_make_cache_key_different(self):
        k1 = _make_cache_key("test", "a")
        k2 = _make_cache_key("test", "b")
        assert k1 != k2

    def test_make_cache_key_different_prefix(self):
        k1 = _make_cache_key("prefix1", "arg")
        k2 = _make_cache_key("prefix2", "arg")
        assert k1 != k2
