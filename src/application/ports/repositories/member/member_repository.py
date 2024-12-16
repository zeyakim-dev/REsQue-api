from abc import abstractmethod
from typing import Optional

from src.application.ports.repositories.repository import Repository
from src.domain.member.entity.member import Member


class MemberRepository(Repository[Member]):
    """User 엔티티를 위한 Repository"""

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[Member]:
        """사용자명으로 사용자 조회"""
        pass

    @abstractmethod
    def exists_by_username(self, username: str) -> bool:
        """사용자명 존재 여부 확인"""
        pass
