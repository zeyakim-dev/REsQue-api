from dataclasses import dataclass
from enum import Enum
from src.domain.member.exceptions import (
    InvalidPlainPasswordException,
    InvalidUsernameException,
    InvalidEmailException
)
from src.domain.shared.base.value import Value

@dataclass(frozen=True)
class Username(Value):
    """사용자 이름을 나타내는 값 객체입니다."""
    value: str
    
    MIN_LENGTH: int = 3
    MAX_LENGTH: int = 50
    ALLOW_SPECIAL_CHARS: bool = False

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise InvalidUsernameException(self.value, "사용자명은 문자열이어야 합니다")
        
        if not (self.MIN_LENGTH <= len(self.value) <= self.MAX_LENGTH):
            raise InvalidUsernameException(
                self.value, 
                f"사용자명은 최소 {self.MIN_LENGTH}자 이상, "
                f"최대 {self.MAX_LENGTH}자 이하여야 합니다"
            )

        if not self.ALLOW_SPECIAL_CHARS and not self.value.isalnum():
            raise InvalidUsernameException(
                self.value, 
                "사용자명은 알파벳과 숫자만 포함할 수 있습니다"
            )

@dataclass(frozen=True)
class HashedPassword(Value):
    """해시된 비밀번호를 나타내는 값 객체입니다."""
    value: str

@dataclass(frozen=True)
class PlainPassword(Value):
    """평문 비밀번호를 나타내는 값 객체입니다."""
    value: str
    
    # 비밀번호 관련 상수를 클래스 변수로 정의
    MIN_LENGTH: int = 8
    REQUIRE_UPPERCASE: bool = True
    REQUIRE_LOWERCASE: bool = True
    REQUIRE_NUMBER: bool = True

    def __post_init__(self):
        if not self._is_valid(self.value):
            raise InvalidPlainPasswordException(
                f"비밀번호는 {self.MIN_LENGTH}자 이상이며, "
                "대소문자와 숫자를 포함해야 합니다"
            )

    def _is_valid(self, value: str) -> bool:
        return (
            isinstance(value, str)
            and len(value) >= self.MIN_LENGTH
            and (not self.REQUIRE_UPPERCASE or any(c.isupper() for c in value))
            and (not self.REQUIRE_LOWERCASE or any(c.islower() for c in value))
            and (not self.REQUIRE_NUMBER or any(c.isdigit() for c in value))
        )

@dataclass(frozen=True)
class Email(Value):
    """이메일 주소를 나타내는 값 객체입니다."""
    value: str
    
    # 이메일 관련 상수를 클래스 변수로 정의
    MAX_LENGTH: int = 255

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise InvalidEmailException("이메일은 문자열이어야 합니다")
            
        if len(self.value) > self.MAX_LENGTH:
            raise InvalidEmailException(
                f"이메일은 {self.MAX_LENGTH}자를 초과할 수 없습니다"
            )

class MemberStatus(Enum):
    """회원 상태를 나타내는 열거형입니다."""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"  
    WITHDRAWN = "WITHDRAWN"

    def can_login(self) -> bool:
        """로그인 가능 여부를 반환합니다."""
        return self == MemberStatus.ACTIVE

    def can_reactivate(self) -> bool:
        """계정 재활성화 가능 여부를 반환합니다."""
        return self == MemberStatus.INACTIVE

class MemberAuthority(Enum):
    """회원 권한을 나타내는 열거형입니다."""
    MEMBER = "MEMBER"
    ADMIN = "ADMIN"

@dataclass(frozen=True)
class AuthenticationFailedCount:
    """인증 실패 횟수를 관리하는 값 객체입니다."""
    value: int = 0
    
    # 로그인 시도 관련 상수를 클래스 변수로 정의
    MAX_ATTEMPTS: int = 5
    
    def increment(self) -> 'AuthenticationFailedCount':
        """실패 횟수를 증가시킨 새로운 인스턴스를 반환합니다."""
        return AuthenticationFailedCount(self.value + 1)
    
    def is_exceeded(self) -> bool:
        """실패 횟수가 제한을 초과했는지 확인합니다."""
        return self.value >= self.MAX_ATTEMPTS
    
    def reset(self) -> 'AuthenticationFailedCount':
        """실패 횟수를 초기화한 새로운 인스턴스를 반환합니다."""
        return AuthenticationFailedCount(0)