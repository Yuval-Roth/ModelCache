from cachetools import Cache
from collections import OrderedDict

class ARC(Cache):
    """
    Adaptive Replacement Cache (ARC) implementation extending cachetools.Cache.

    This class implements the ARC algorithm, which balances between recency (LRU)
    and frequency (LFU-like behavior) by maintaining two active lists (T1, T2)
    and two ghost lists (B1, B2). It adaptively adjusts the target size for T1 (p)
    based on cache hits in the ghost lists.

    The implementation overrides __getitem__, __setitem__, and __missing__
    to integrate ARC's specific logic with the cachetools interface.
    """
    def __init__(self, maxsize, getsizeof=None):
        """
        Initializes the ARC cache.

        Args:
            maxsize (int): The maximum number of items the cache can hold.
            getsizeof (callable, optional): A function that returns the size
                                            of an item. If None, all items are
                                            considered to have a size of 1.
        """
        super().__init__(maxsize, getsizeof)

        # T1: List for items seen only once (recently accessed)
        self.t1 = OrderedDict()
        # T2: List for items seen multiple times (frequently accessed)
        self.t2 = OrderedDict()

        # B1: Ghost list for T1 (stores keys of items recently evicted from T1)
        self.b1 = OrderedDict()
        # B2: Ghost list for T2 (stores keys of items recently evicted from T2)
        self.b2 = OrderedDict()

        # p: Adaptive parameter controlling the target size of T1.
        # It balances between favoring T1 (recency) and T2 (frequency).
        # p ranges from 0 to maxsize.
        self.p = 0

    def __len__(self):
        """
        Returns the current number of items in the active cache (T1 + T2).
        """
        return len(self.t1) + len(self.t2)

    def __contains__(self, key):
        """
        Checks if a key is present in the active cache (T1 or T2).
        """
        return key in self.t1 or key in self.t2

    def _evict_internal(self):
        """
        Internal eviction logic for ARC.
        This method ensures the total cache size (T1 + T2) does not exceed `maxsize`
        and manages the sizes of the ghost lists (B1, B2).
        """
        # Step 1: Evict from T1 or T2 if the total cache size exceeds maxsize
        while len(self.t1) + len(self.t2) > self.maxsize:
            # Evict from T1 if it's larger than its target size 'p',
            # or if T1 is empty and T2 is not.
            if len(self.t1) > self.p or (len(self.t1) == 0 and len(self.t2) > 0):
                # Evict LRU item from T1 and move its key to B1
                key, value = self.t1.popitem(last=False)
                self.b1[key] = value # Store value in ghost for potential re-insertion
            else:
                # Evict LRU item from T2 and move its key to B2
                key, value = self.t2.popitem(last=False)
                self.b2[key] = value # Store value in ghost for potential re-insertion

        # Step 2: Maintain the sizes of the ghost lists (B1 and B2)
        # According to the PDF's diagram, |B1| <= maxsize - p and |B2| <= p.
        # If a ghost list exceeds its capacity, its LRU item is removed.
        while len(self.b1) > (self.maxsize - self.p):
            self.b1.popitem(last=False)
        while len(self.b2) > self.p:
            self.b2.popitem(last=False)

    def __setitem__(self, key, value):
        """
        Handles insertions and updates for ARC.
        This method is called by the base Cache class after __missing__ returns a value,
        or for direct assignments (e.g., cache[key] = value).
        """
        # Remove the key from any existing lists to ensure correct placement
        # and prevent duplicates if it's being re-inserted or updated.
        if key in self.t1:
            del self.t1[key]
        if key in self.t2:
            del self.t2[key]
        if key in self.b1:
            del self.b1[key]
        if key in self.b2:
            del self.b2[key]

        # For direct assignments or after a true cold miss (handled by __missing__),
        # the item is initially placed in T1 (as per ARC's OnMiss logic).
        self.t1[key] = value
        self.t1.move_to_end(key) # Mark as most recently used in T1
        self._evict_internal()

    def __getitem__(self, key):
        """
        Retrieves an item from the cache, implementing ARC's hit/miss logic
        and adaptive parameter 'p' adjustment.
        """
        # Case 1: Cache Hit in T1
        if key in self.t1:
            value = self.t1.pop(key)
            self.t2[key] = value  # Move item from T1 to T2
            self.t2.move_to_end(key) # Mark as most recently used in T2
            self.p = max(0, self.p - 1) # Adjust 'p' as per PDF's OnHit(T1) logic
            self._evict_internal()
            return value

        # Case 2: Cache Hit in T2
        if key in self.t2:
            value = self.t2.pop(key)
            self.t2[key] = value  # Move item to end of T2 (update recency)
            self.t2.move_to_end(key)
            self.p = min(self.maxsize, self.p + 1) # Adjust 'p' as per PDF's OnHit(T2) logic
            self._evict_internal()
            return value

        # Case 3: Cache Miss - Check Ghost Lists (B1, B2)
        # If a key is found in a ghost list, it's a "ghost hit".
        # We fetch the value from the source and promote it to T2.
        if key in self.b1:
            del self.b1[key] # Remove from B1
            self.p = min(self.maxsize, self.p + 1) # Adjust 'p'
            self._evict_internal() # Evict to make space if needed

            # Fetch the actual value from the underlying data source.
            # This calls the base Cache's __missing__ which should be overridden
            # by the user to provide the data fetching logic.
            value = super().__missing__(key)

            self.t2[key] = value # Insert into T2
            self.t2.move_to_end(key)
            return value

        if key in self.b2:
            del self.b2[key] # Remove from B2
            self.p = max(0, self.p - 1) # Adjust 'p'
            self._evict_internal() # Evict to make space if needed

            # Fetch the actual value from the underlying data source.
            value = super().__missing__(key)

            self.t2[key] = value # Insert into T2
            self.t2.move_to_end(key)
            return value

        # Case 4: Cold Miss (not in T1, T2, B1, or B2)
        # Let the base Cache's __getitem__ handle this. It will call __missing__
        # to fetch the value, and then __setitem__ to place it in T1.
        return super().__getitem__(key)

    def __missing__(self, key):
        """
        This method is called by the base Cache's __getitem__ when a key is
        not found in the cache (and not a ghost hit handled by our __getitem__).

        It's responsible for fetching the value from the original data source.
        In a real application, you would replace this with your data retrieval logic.
        """
        print(f"DEBUG: Fetching '{key}' from external source (cold miss).")
        # Simulate fetching from a source. Replace this with your actual data source logic.
        return f"Value_for_{key}"

    def pop(self, key, default=None):
        """
        Removes and returns an item from the cache.
        """
        if key in self.t1:
            return self.t1.pop(key)
        if key in self.t2:
            return self.t2.pop(key)
        if key in self.b1: # Can also remove from ghost lists if needed
            return self.b1.pop(key)
        if key in self.b2:
            return self.b2.pop(key)
        return default

    def clear(self):
        """
        Clears all cache lists (T1, T2, B1, B2) and resets the adaptive parameter 'p'.
        """
        self.t1.clear()
        self.t2.clear()
        self.b1.clear()
        self.b2.clear()
        self.p = 0
        super().clear() # Also clear the base cache's internal dictionary

    def __iter__(self):
        """
        Iterates over the keys currently in the active cache (T1 then T2).
        """
        yield from self.t1
        yield from self.t2

    def __repr__(self):
        """
        Provides a string representation of the ARC cache's state.
        """
        return (f"ARC(maxsize={self.maxsize}, p={self.p}, len={len(self)}, "
                f"t1_len={len(self.t1)}, t2_len={len(self.t2)}, "
                f"b1_len={len(self.b1)}, b2_len={len(self.b2)})")

