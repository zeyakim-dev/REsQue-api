from abc import ABC, abstractmethod
from typing import Generic, Optional, Set, TypeVar
from uuid import UUID

from src.domain.entity import Entity

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """기본 Repository 추상 클래스"""

    def __init__(self):
        self.seen: Set[Entity] = set()

    def add(self, entity: Entity):
        self._add(entity)
        self.seen.add(entity)

    def get(self, id: UUID) -> Entity:
        entity = self._get(id)
        if entity:
            self.seen.add(entity)
        return entity

    @abstractmethod
    def _add(self, entity: Entity):
        raise NotImplementedError

    @abstractmethod
    def _get(self, id: UUID):
        raise NotImplementedError
