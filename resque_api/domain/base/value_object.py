from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Generic, Iterator, Self, TypeVar

from collections.abc import Collection

from resque_api.domain.base.exceptions import DuplicateItemFoundError, ItemNotFoundError

T = TypeVar("T")

@dataclass(frozen=True)
class ValueObject(Generic[T]):
    value: T

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return NotImplemented
        return self.value == other.value


class BaseVOCollection(Collection[T]):
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

L = TypeVar("L")

@dataclass(frozen=True)
class VOList(BaseVOCollection[list], Generic[L]):
    """VO의 리스트를 관리하는 불변 컬렉션"""

    values: tuple[L, ...] = field(default_factory=tuple)

    def add(self, item: L) -> Self:
        """새로운 아이템을 추가한 새로운 VOList 반환 (불변 유지)"""
        if item in self.values:
            raise DuplicateItemFoundError(f"Item '{item}' is duplicated.")
        return VOList((*self.values, item))

    def remove(self, item: L) -> Self:
        """아이템을 제거한 새로운 VOList 반환 (불변 유지)"""
        if item not in self.values:
            raise ItemNotFoundError(f"Item '{item}' not found in VOList.")
        return VOList(tuple(v for v in self.values if v != item))

    def as_list(self) -> list[L]:
        """리스트 형태로 반환"""
        return list(self.values)

K = TypeVar("K")
V = TypeVar("V")

@dataclass(frozen=True)
class VODict(BaseVOCollection[dict], Generic[K, V]):
    """VO의 딕셔너리를 관리하는 불변 컬렉션"""

    values: dict[K, V] = field(default_factory=dict)

    def add(self, key: K, value: V) -> Self:
        """새로운 키-값 쌍을 추가한 새로운 VODict 반환 (불변 유지)"""
        return VODict({**self.values, key: value})

    def remove(self, key: K) -> Self:
        """키-값 쌍을 제거한 새로운 VODict 반환 (불변 유지)"""
        if key not in self.values:
            raise ItemNotFoundError(f"Key '{key}' not found in VODict.")
        return VODict({k: v for k, v in self.values.items() if key != k})

    def as_dict(self) -> dict[K, V]:
        """딕셔너리 형태로 반환"""
        return self.values
