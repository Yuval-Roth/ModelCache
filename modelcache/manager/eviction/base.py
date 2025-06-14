# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod
from typing import Any, List, Tuple


class EvictionBase(metaclass=ABCMeta):
    """
    Eviction base.
    """

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
    def flush(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @property
    @abstractmethod
    def policy(self) -> str:
        pass
