from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic
from uuid import UUID

T = TypeVar('T')  # 엔티티 타입을 위한 타입 변수

class Repository(ABC, Generic[T]):
    """기본 Repository 추상 클래스"""
    
    @abstractmethod
    def save(self, entity: T) -> None:
        """엔티티 저장 또는 수정"""
        pass
    
    @abstractmethod
    def find_by_id(self, id: UUID) -> Optional[T]:
        """ID로 엔티티 조회"""
        pass