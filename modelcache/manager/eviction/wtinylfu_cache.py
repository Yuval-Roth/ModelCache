from cachetools import LRUCache, Cache, LFUCache
from readerwriterlock import rwlock
import random

class CountMinSketch:
    def __init__(self, width=1024, depth=4, decay_interval=10000):
        self.width = width
        self.depth = depth
        self.tables = [[0]*width for _ in range(depth)]
        self.seeds = [random.randrange(1<<30) for _ in range(depth)]
        self.ops = 0
        self.decay_interval = decay_interval

    def _hash(self, x, seed):
        return hash((x, seed)) % self.width

    def add(self, x):
        self.ops += 1
        est = self.estimate(x)
        for i, seed in enumerate(self.seeds):
            idx = self._hash(x, seed)
            if self.tables[i][idx] <= est:
                self.tables[i][idx] += 1
        if self.ops >= self.decay_interval:
            self.decay()
            self.ops = 0

    def estimate(self, x):
        return min(self.tables[i][self._hash(x, seed)]
                   for i, seed in enumerate(self.seeds))

    def decay(self):
        for table in self.tables:
            for i in range(len(table)):
                table[i] >>= 1

class W2TinyLFU(Cache):
    def __init__(self, maxsize, window_pct=0.01):
        """
        param maxsize: Maximum size of the cache.

        param window_pct: Percentage of the cache size to be used for the window.
        """
        super().__init__(maxsize)
        self.window_size = max(1, int(maxsize * window_pct))
        rest = maxsize - self.window_size
        self.probation_size = rest // 2
        self.protected_size = rest - self.probation_size

        self.window = LRUCache(maxsize=self.window_size)
        self.probation = LFUCache(maxsize=self.probation_size)
        self.protected = LFUCache(maxsize=self.protected_size)

        self.cms = CountMinSketch()
        self.data = {}
        self._rw_lock = rwlock.RWLockWrite()

    def __setitem__(self, key, value):
        with self._rw_lock.gen_wlock():
            self.data[key] = value
            self._put(key)

    def __getitem__(self, key):
        val = self.get(key, default=None)
        if val is None:
            raise KeyError(key)
        return val

    def __contains__(self, key):
        return key in self.window or key in self.probation or key in self.protected

    def __delitem__(self, key):
        with self._rw_lock.gen_wlock():
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
                demoted = next(iter(self.protected))
                self.protected.pop(demoted)
                self.probation[demoted] = True
            self.protected[key] = True
            return self.data.get(key, default)
        return default

    def _put(self, key):
        self.cms.add(key)
        if key in self:
            return

        if len(self.window) < self.window_size:
            self.window[key] = True
            return

        victim = next(iter(self.window))
        self.window.pop(victim)

        if self.cms.estimate(key) >= self.cms.estimate(victim):
            self._admit_to_main(victim)
            self._admit_to_main(key)
        else:
            self._admit_to_main(victim)
            self.data.pop(key, None)

    def _admit_to_main(self, key):
        if key in self.protected or key in self.probation:
            return
        if self.probation_size == 0:
            self.data.pop(key, None)
            return
        if len(self.probation) < self.probation_size:
            self.probation[key] = True
        elif self.probation:
            evicted = next(iter(self.probation))
            self.probation.pop(evicted)
            self.probation[key] = True
            self.data.pop(evicted, None)
        else:
            self.data.pop(key, None)

    def clear(self):
        with self._rw_lock.gen_wlock():
            self.window.clear()
            self.probation.clear()
            self.protected.clear()
            self.data.clear()