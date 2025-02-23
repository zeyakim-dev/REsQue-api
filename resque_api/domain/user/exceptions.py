class InvalidPasswordError(Exception):
    """잘못된 비밀번호 예외"""

    pass

class InactiveUserError(Exception):
    """비활성 사용자 작업 시도 예외"""

    pass
