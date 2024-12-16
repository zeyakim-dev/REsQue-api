from dataclasses import dataclass, replace
from typing import List

from src.application.ports.security.password_hasher import PasswordHasher
from src.domain.shared.base.aggregate import Aggregate
from src.domain.member.values import AuthenticationFailedCount, Email, LoginAttempt, MemberAuthority, MemberStatus, HashedPassword, PlainPassword, Username


@dataclass(frozen=True)
class Member(Aggregate):
    """회원을 나타내는 애그리게잇 루트 엔티티입니다.
    
    Attributes:
        username (Username): 회원 이름. 시스템 내에서 고유한 값이어야 합니다.
        password (Password): 암호화된 비밀번호. 보안을 위해 해시된 형태로 저장됩니다.
        email (Email): 회원의 이메일 주소. 유효한 이메일 형식이어야 합니다.
        authority (MemberAuthority): 회원의 시스템 권한. 일반 사용자와 관리자를 구분합니다.
        status (MemberStatus): 회원의 현재 상태. 기본값은 ACTIVE입니다.
        login_attempts (List[LoginAttempt]): 로그인 시도 이력. 보안을 위해 실패한 시도를 추적합니다.
    """

    username: Username
    password: HashedPassword
    email: Email
    authority: MemberAuthority
    status: MemberStatus = MemberStatus.ACTIVE
    authentication_failed_count: AuthenticationFailedCount = AuthenticationFailedCount()
    
    def authenticate(self, input_password, password_hasher=PasswordHasher) -> bool:
        """입력받은 비밀번호의 유효성을 검증합니다.
        
        Args:
            input_password (str): 검증할 비밀번호
            password_hasher (AbstractPasswordHasher): 비밀번호 해싱 도구
            
        Returns:
            bool: 비밀번호가 일치하면 True, 그렇지 않으면 False
        """
        return password_hasher.verify(self, input_password, self.password.value)

    def increment_failed_count(self) -> 'Member':
        """인증 실패 횟수를 증가시킨 새로운 Member 인스턴스를 반환합니다.
        
        Returns:
            Member: 인증 실패 횟수가 증가된 새로운 Member 인스턴스
        """
        return replace(
            self, 
            authentication_failed_count=self.authentication_failed_count.increment()
        )

    def reset_failed_count(self) -> 'Member':
        """인증 실패 횟수를 초기화한 새로운 Member 인스턴스를 반환합니다.
        
        Returns:
            Member: 인증 실패 횟수가 초기화된 새로운 Member 인스턴스
        """
        return replace(
            self, 
            authentication_failed_count=self.authentication_failed_count.reset()
        )

    def inactivate_by_admin(self, admin: 'Member') -> 'Member':
        """관리자에 의한 계정 비활성화를 수행합니다.
        
        Args:
            admin (Member): 비활성화를 요청한 관리자 회원
            
        Raises:
            PermissionError: 관리자 권한이 없는 회원이 요청한 경우
        """
        if not admin.authority == MemberAuthority.ADMIN:
            raise PermissionError
        return self.inactivate()

    def inactivate(self) -> 'Member':
        """회원 계정을 비활성화한 새로운 Member 인스턴스를 반환합니다.
        
        Returns:
            Member: 비활성화된 상태의 새로운 Member 인스턴스
        """
        return replace(self, status=MemberStatus.INACTIVE)
    
    def is_too_many_attempts(self) -> bool:
        """인증 실패 횟수가 제한을 초과했는지 확인합니다.
        
        Returns:
            bool: 인증 실패 횟수가 제한을 초과하면 True, 그렇지 않으면 False
        """
        return self.authentication_failed_count.is_exceeded()