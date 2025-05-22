from cachetools import LRUCache, Cache
import random
from typing import Any, Callable

class CountMinSketch:
    def __init__(self, width=1024, depth=4):
        self.width = width
        self.depth = depth
        self.tables = [[0] * width for _ in range(depth)]
        self.seeds = [random.randint(0, 2**31) for _ in range(depth)]

    def _hash(self, x, seed):
        return hash((x, seed)) % self.width

    def add(self, x):
        for i, seed in enumerate(self.seeds):
            self.tables[i][self._hash(x, seed)] += 1

    def estimate(self, x):
        return min(self.tables[i][self._hash(x, seed)] for i, seed in enumerate(self.seeds))

    def decay(self):
        for row in self.tables:
            for i in range(len(row)):
                row[i] >>= 1


class WTinyLFUEviction(Cache):
    def __init__(self, maxsize, window_percent=1, on_evict: Callable[[list], None] = None):
        super().__init__(maxsize)
        self.window_size = max(1, int(maxsize * window_percent / 100))
        self.probation_size = (maxsize - self.window_size) // 2
        self.protected_size = maxsize - self.window_size - self.probation_size

        self.window = LRUCache(maxsize=self.window_size)
        self.probation = LRUCache(maxsize=self.probation_size)
        self.protected = LRUCache(maxsize=self.protected_size)

        self.cms = CountMinSketch()
        self.on_evict = on_evict

        # optional: actual values stored here
        self.data = {}

    # -----------------------------------------
    # Dict-like API (required by Cache base class)
    # -----------------------------------------

    def __setitem__(self, key, value):
        self.data[key] = value
        self.put(key)

    def __getitem__(self, key):
        if self.get(key) is not None:
            return self.data[key]
        raise KeyError(key)

    def __contains__(self, key):
        return key in self.window or key in self.protected or key in self.probation

    def __delitem__(self, key):
        self.data.pop(key, None)
        self.window.pop(key, None)
        self.probation.pop(key, None)
        self.protected.pop(key, None)

    def get(self, key, default=None):
        if key in self.window:
            self.window[key] = True
            return self.data.get(key, default)
        if key in self.protected:
            self.protected[key] = True
            return self.data.get(key, default)
        if key in self.probation:
            self.probation.pop(key)
            if len(self.protected) >= self.protected_size:
                evicted = next(iter(self.protected))
                self.protected.pop(evicted)
                self.data.pop(evicted, None)
            self.protected[key] = True
            return self.data.get(key, default)
        return default

    # -----------------------------------------
    # W-TinyLFU Logic
    # -----------------------------------------

    def put(self, key: Any):
        self.cms.add(key)

        if key in self:
            return

        if len(self.window) < self.window_size:
            self.window[key] = True
            return

        victim = next(iter(self.window))
        self.window.pop(victim)

        if self.cms.estimate(key) >= self.cms.estimate(victim):
            evicted = self._add_to_main_cache(key)
            if self.on_evict and evicted:
                self.on_evict([evicted])
                self.data.pop(evicted, None)
            self._add_to_main_cache(victim)
        else:
            self._add_to_main_cache(victim)
            if self.on_evict:
                self.on_evict([key])
                self.data.pop(key, None)

    def _add_to_main_cache(self, key):
        if key in self.protected or key in self.probation:
            return None
        if len(self.probation) < self.probation_size:
            self.probation[key] = True
            return None
        evicted = next(iter(self.probation))
        self.probation.pop(evicted)
        self.probation[key] = True
        return evicted
