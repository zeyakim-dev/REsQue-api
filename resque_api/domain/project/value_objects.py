from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import secrets
from typing import Self

from resque_api.domain.project.exceptions import InvalidTitleError
from resque_api.domain.common.value_objects import ValueObject


class ProjectStatus(Enum):
    """프로젝트 상태"""

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"


class ProjectRole(Enum):
    """프로젝트 멤버 역할"""

    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class InvitationStatus(Enum):
    """초대 상태"""

    PENDING = "PENDING"  # 초대 발송 후 대기 중
    ACCEPTED = "ACCEPTED"  # 초대 수락 완료
    EXPIRED = "EXPIRED"  # 초대 만료
    REVOKED = "REVOKED"  # 초대 취소


@dataclass(frozen=True)
class ProjectTitle(ValueObject[str]):
    """프로젝트 제목 VO"""

    value: str

    def __post_init__(self):
        if not self.value:
            raise InvalidTitleError("Title cannot be empty")
        if len(self.value) < 3:
            raise InvalidTitleError("Title is too short")
        if len(self.value) > 100:
            raise InvalidTitleError("Title is too long")


@dataclass(frozen=True)
class InvitationCode(ValueObject[str]):
    """초대 코드 VO"""

    value: str

    @classmethod
    def generate(cls) -> Self:
        """안전한 초대 코드 생성"""
        return cls(secrets.token_urlsafe(32))
    
    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class InvitationExpiration(ValueObject[datetime]):
    """초대 유효 기간 VO"""
    
    value: datetime

    @classmethod
    def create(cls, days: int = 7) -> Self:
        """초대 유효 기간을 현재 시간 기준으로 설정"""

        expiration_date = datetime.now(timezone.utc) + timedelta(days=days)
        return cls(value=expiration_date)

    def is_expired(self) -> bool:
        """초대 코드가 만료되었는지 확인"""
        return datetime.now(timezone.utc) > self.value