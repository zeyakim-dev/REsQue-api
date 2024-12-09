from abc import ABC, abstractmethod
from typing import Generic, Optional, Set, TypeVar
from uuid import UUID

from src.domain.shared.aggregate_root import AggregateRoot


T = TypeVar("T", bound=AggregateRoot)


class Repository(ABC, Generic[T]):
    """기본 Repository 추상 클래스"""

    def __init__(self):
        self.seen: Set[T] = set()

    def add(self, aggregate: T) -> None:
        self._add(aggregate)
        self.seen.add(aggregate)

    def get(self, id: UUID) -> Optional[T]:
        aggregate = self._get(id)
        if aggregate:
            self.seen.add(aggregate)
        return aggregate

    @abstractmethod
    def _add(self, aggregate: T) -> None:
        raise NotImplementedError

    @abstractmethod
    def _get(self, id: UUID) -> Optional[T]:
        raise NotImplementedError