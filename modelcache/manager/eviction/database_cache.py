# -*- coding: utf-8 -*-
from typing import Any, Callable, List, Tuple
import cachetools

from modelcache.manager.eviction.base import EvictionBase
from modelcache_mm.manager.scalar_data.base import CacheData
from modelcache_mm.manager.vector_data.base import VectorData
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

    def create_vector(self, model: str):
        self.vector_storage.create(model)

    def put(self, obj: Tuple[Any, Any], model: str):
        pass

    def batch_put(self, objs: List[Tuple[Any, Any]], model: str):
        cache_datas = []
        vector_datas = []
        for key, value in objs:
            if isinstance(value, tuple) and len(value) == 4:
                answer, question, embedding_data, model_name = value
                cache_datas.append(CacheData(question=question, answers=[answer], embedding_data=embedding_data))
            else:
                raise ValueError("Each value must be a tuple (answer, question, embedding_data, model)")
        scalar_ids = self.scalar_storage.batch_insert(cache_datas)
        for idx, (key, value) in enumerate(objs):
            embedding_data = value[2]
            if scalar_ids and embedding_data is not None:
                vector_datas.append(VectorData(id=scalar_ids[idx], data=embedding_data))
        if vector_datas:
            self.vector_storage.mul_add(vector_datas, model=model)
        return scalar_ids

    def insert_query_resp(self, query_resp_dict: Any, **kwargs):
        self.scalar_storage.insert_query_resp(query_resp_dict, **kwargs)

    def update_hit_count_by_id(self, primary_id: Any):
        self.scalar_storage.update_hit_count_by_id(primary_id)

    def get(self, obj: Any, model: str):
        return self.scalar_storage.get_data_by_id(obj)

    def search(self, data: Any, top_k: int, model: str):
        return self.vector_storage.search(data, top_k=top_k, model=model)

    def delete(self, id_list: Any, model: str):
        scalar_count = -1
        vector_count = -1
        try:
            vector_count = self.vector_storage.delete(id_list, model=model)
        except Exception as e:
            vector_count = -1
        try:
            scalar_count = self.scalar_storage.mark_deleted(id_list)
        except Exception as e:
            scalar_count = -1
        return scalar_count, vector_count

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
