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


@dataclass(frozen=True)
class VOList(Collection[T], Generic[T]):
    """VO의 리스트를 관리하는 불변 컬렉션"""

    values: tuple[T, ...] = field(default_factory=tuple)

    def __iter__(self) -> Iterator[T]:
        """리스트 순회 지원"""
        return iter(self.values)

    def __contains__(self, item: T) -> bool:
        """해당 아이템이 리스트에 존재하는지 확인"""
        return item in self.values

    def __len__(self) -> int:
        """리스트 길이 반환"""
        return len(self.values)

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