from typing import Any, Callable


class LRUEvictionPolicy:
    """
    Implements a Least Recently Used (LRU) eviction policy for managing cache entries.
    This policy evicts the least recently used entry when the policy exceeds its capacity.
    """
    def __init__(self, capacity: int, on_evict: Callable[[Any],None]):
        """
        :param capacity: Maximum number of entries the cache can hold.
        :param on_evict: Callback function to call when an entry is evicted.
        """
        self.on_evict = on_evict
        self.capacity = capacity
        self.cache: dict[Any, LRUEvictionPolicy.LinkedNode] = {}
        self.order = LRUEvictionPolicy.DoublyLinkedList()
        self.size = 0

    def touch(self, key):
        """
        Marks the entry as most recently used.
        """
        if key not in self.cache:
            return
        node = self.cache[key]
        self.order.remove(node)
        self.order.add(node)

    def add(self, key):
        """
        Adds a new entry to the policy.
        If the policy exceeds its capacity, it evicts the least recently used entry.
        Calling this method with an existing key is the same as calling `touch`.
        """
        if key in self.cache:
            self.touch(key)
            return

        if self.size >= self.capacity:
            self.evict()
        node = LRUEvictionPolicy.LinkedNode(key)
        self.cache[key] = node
        self.order.add(node)
        self.size += 1

    def evict(self):
        """
        Evicts the least recently used entry from the cache and the order list.
        """
        if self.size == 0:
            return
        victim = self.order.head
        self.order.remove(victim)
        del self.cache[victim.key]
        self.size -= 1
        self.on_evict(victim.key)

    def truncate(self):
        """
        clears all entries from the policy.
        """
        self.cache.clear()
        self.order = LRUEvictionPolicy.DoublyLinkedList()
        self.size = 0

    class LinkedNode:
        def __init__(self, key):
            self.key = key
            self.prev = None
            self.next = None

    class DoublyLinkedList:
        def __init__(self):
            self.head = None
            self.tail = None

        def add(self, new_node):
            if not self.head:
                self.head = new_node
                self.tail = new_node
            else:
                new_node.prev = self.tail
                self.tail.next = new_node
                self.tail = new_node

        def remove(self, node):
            if not node.prev:
                self.head = node.next
            else:
                node.prev.next = node.next

            if not node.next:
                self.tail = node.prev
            else:
                node.next.prev = node.prev






