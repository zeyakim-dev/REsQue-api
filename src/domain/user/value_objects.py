from dataclasses import dataclass
from enum import Enum

class AuthProvider(Enum):
    """인증 제공자"""
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"

class UserStatus(Enum):
    """사용자 상태"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

@dataclass(frozen=True)
class Password:
    """비밀번호 값 객체"""
    hashed_value: str

    def __post_init__(self):
        """비밀번호 정책 검증"""
        if not self.hashed_value:
            raise ValueError("Password hash cannot be empty")

    def equals(self, other: 'Password') -> bool:
        """비밀번호 일치 여부 검증"""
        return self.hashed_value == other.hashed_value 