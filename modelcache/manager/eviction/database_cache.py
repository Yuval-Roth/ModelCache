# -*- coding: utf-8 -*-
from typing import Any, Callable, List, Tuple
import cachetools

from modelcache.manager.eviction.base import EvictionBase
from .arc_cache import ARC
from .wtinylfu_cache import W2TinyLFU
from ..scalar_data.base import ScalarStorage
from ..vector_data.base import VectorStorage


class DatabaseCache(EvictionBase):

    def __init__(self, policy: str, maxsize: int, clean_size: int, scalar_storage: ScalarStorage, vector_storage: VectorStorage, **kwargs):
        self._policy = policy.upper()
        self.maxsize = maxsize
        self.clean_size = clean_size
        self.kwargs = kwargs
        self.scalar_storage = scalar_storage
        self.vector_storage = vector_storage

    def put(self, obj: Tuple[Any, Any], model: str):
        pass

    def batch_put(self, objs: List[Tuple[Any, Any]], model: str):
        pass

    def get(self, obj: Any, model: str):
        pass

    def clear(self, model: str):
        pass

    def flush(self):
        self.scalar_storage.flush()
        self.vector_storage.flush()

    def close(self):
        self.scalar_storage.close()
        self.vector_storage.close()


    @property
    def policy(self) -> str:
        return self._policy
