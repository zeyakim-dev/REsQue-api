from src.domain.domain_exception import DomainException

class UserDomainException(DomainException):
    """사용자 도메인과 관련된 모든 예외의 기본 클래스입니다."""
    pass

class InvalidUsernameException(UserDomainException):
    """유효하지 않은 사용자명일 때 발생하는 예외입니다."""
    def __init__(self, username: str, reason: str):
        self.username = username
        super().__init__(
            f"유효하지 않은 사용자명입니다: '{username}'. "
            f"원인: {reason}"
        )

class InvalidPasswordException(UserDomainException):
    """유효하지 않은 비밀번호일 때 발생하는 예외입니다."""
    def __init__(self, reason: str):
        # 보안상 실제 비밀번호는 예외 메시지에 포함하지 않습니다
        super().__init__(
            f"유효하지 않은 비밀번호입니다. "
            f"원인: {reason}"
        )

class UserNotFoundException(UserDomainException):
    """사용자를 찾을 수 없을 때 발생하는 예외입니다."""
    def __init__(self, identifier: str):
        super().__init__(f"사용자를 찾을 수 없습니다: {identifier}")

class DuplicateUsernameException(UserDomainException):
    """이미 존재하는 사용자명으로 가입을 시도할 때 발생하는 예외입니다."""
    def __init__(self, username: str):
        super().__init__(f"이미 사용 중인 사용자명입니다: {username}")

class AuthenticationFailedException(UserDomainException):
    """인증 실패 시 발생하는 예외입니다."""
    def __init__(self):
        # 보안상 구체적인 실패 이유는 노출하지 않습니다
        super().__init__("사용자명 또는 비밀번호가 올바르지 않습니다")