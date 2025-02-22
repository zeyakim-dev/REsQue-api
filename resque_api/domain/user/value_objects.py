import re
from dataclasses import dataclass
from enum import Enum

from resque_api.domain.base.value_object import ValueObject
from resque_api.domain.user.exceptions import InvalidEmailError, InvalidPasswordError


class AuthProvider(Enum):
    """인증 제공자"""

    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"


class UserStatus(Enum):
    """사용자 상태"""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


@dataclass(frozen=True)
class Password(ValueObject[str]):
    """비밀번호 값 객체"""

    def __post_init__(self):
        """비밀번호 검증 수행"""
        super().__post_init__()
        self._validate_password()

    def _validate_password(self) -> None:
        """비밀번호 해시 값 검증"""
        if not self.value or len(self.value) < 10:  # 길이 체크 추가
            raise InvalidPasswordError("Password hash must be at least 10 characters long")
