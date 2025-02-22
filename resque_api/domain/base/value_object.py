from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Iterator, Self, TypeVar

from collections.abc import Collection

from resque_api.domain.base.exceptions import ItemNotFoundError

T = TypeVar("T")

@dataclass(frozen=True)
class ValueObject(Generic[T]):
    value: T

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return NotImplemented
        return self.value == other.value


class BaseVOCollection(Collection[T], Generic[T]):
    """Value Object 컬렉션을 위한 기본 추상 클래스"""

    values: Collection[T]

    @abstractmethod
    def add(self, item: T) -> Self:
        """아이템을 컬렉션에 추가하고 새로운 컬렉션 반환"""
        pass

    @abstractmethod
    def remove(self, item: T) -> Self:
        """아이템을 컬렉션에서 제거하고 새로운 컬렉션 반환"""
        pass

    def __contains__(self, item: T) -> bool:
        """해당 아이템이 컬렉션에 포함되어 있는지 확인"""
        return item in self.values

    def __len__(self) -> int:
        """컬렉션의 길이 반환"""
        return len(self.values)

    def __iter__(self) -> Iterator[T]:
        """컬렉션 순회"""
        return iter(self.values)


@dataclass(frozen=True)
class VOList(Collection[T], Generic[T]):
    """VO의 리스트를 관리하는 불변 컬렉션"""

    values: tuple[T, ...] = field(default_factory=tuple)

    def add(self, item: T) -> Self:
        """새로운 아이템을 추가한 새로운 VOList 반환 (불변 유지)"""
        if item in self.values:
            return self
        return VOList((*self.values, item))

    def remove(self, item: T) -> Self:
        """아이템을 제거한 새로운 VOList 반환 (불변 유지)"""
        if item not in self.values:
            raise ItemNotFoundError(f"Item '{item}' not found in VOList.")
        return VOList(tuple(v for v in self.values if v != item))

    def as_list(self) -> list[T]:
        """리스트 형태로 반환"""
        return list(self.values)