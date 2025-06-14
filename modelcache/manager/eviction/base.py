# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import Any, List, Tuple


class EvictionBase(metaclass=ABCMeta):
    """
    Eviction base.
    """

    @abstractmethod
    def create_vector(self, model: str):
        pass

    @abstractmethod
    def put(self, obj: Tuple[Any, Any] , model:str):
        pass

    @abstractmethod
    def batch_put(self, obj: List[Tuple[Any, Any]], model: str):
        pass

    @abstractmethod
    def get(self, obj: Any, model:str):
        pass

    @abstractmethod
    def insert_query_resp(self, query_resp_dict: Any, **kwargs):
        pass

    @abstractmethod
    def update_hit_count_by_id(self, primary_id: Any):
        pass

    @abstractmethod
    def search(self, data: Any, top_k: int , model: str):
        pass

    @abstractmethod
    def delete(self, id_list: Any, model: str):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @property
    @abstractmethod
    def policy(self) -> str:
        pass
