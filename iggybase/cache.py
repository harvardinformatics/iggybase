from werkzeug.contrib.cache import SimpleCache
from functools import wraps

class Cache:

    TIMEOUT = 5 * 60

    def __init__(self):
        self.store = SimpleCache()
        self.refresh_keys = {}

    def get(self, cache_key):
        res = self.store.get(cache_key)
        return res

    def set(self, cache_key, val, timeout = TIMEOUT, tbls = []):
        self.set_refresh(cache_key, tbls)
        self.store.set(cache_key, val, timeout)

    def set_refresh(self, cache_key, tbls):
        if tbls:
            self.refresh_keys[cache_key] = tbls
        elif cache_key in self.refresh_keys:
            self.refresh_keys.pop(cache_key, None)

