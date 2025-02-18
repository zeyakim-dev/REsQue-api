from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID
from src.domain.user.value_objects import AuthProvider, UserStatus, Password
from src.domain.user.exceptions import InvalidEmailError, InactiveUserError
import re

@dataclass(frozen=True)
class User:
    """사용자 엔티티
    
    도메인 규칙:
    - 이메일은 유일한 식별자로 사용됨
    - OAuth 사용자는 별도의 인증 로직 사용
    - 비활성 상태의 사용자는 어떤 작업도 수행할 수 없음
    """
    id: UUID
    email: str
    auth_provider: AuthProvider
    status: UserStatus
    created_at: datetime
    password: Password = None

    def __post_init__(self):
        """객체 생성 후 유효성 검증"""
        self._validate_email()

    def _validate_email(self) -> None:
        """이메일 형식 검증"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.email):
            raise InvalidEmailError("Invalid email format")

    def can_authenticate(self) -> bool:
        """인증 가능 여부 확인"""
        if self.status == UserStatus.INACTIVE:
            raise InactiveUserError("Inactive user cannot perform actions")
        
        if self.auth_provider != AuthProvider.EMAIL:
            return False
            
        return self.password is not None

    def update_status(self, new_status: UserStatus) -> 'User':
        """사용자 상태 변경
        
        비활성 상태의 사용자는 상태 변경 불가
        새로운 User 인스턴스를 반환
        """
        if self.status == UserStatus.INACTIVE:
            raise InactiveUserError("Inactive user cannot perform actions")
        return replace(self, status=new_status)