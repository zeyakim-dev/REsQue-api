class InvalidEmailError(Exception):
    """잘못된 이메일 형식 예외"""
    pass

class InactiveUserError(Exception):
    """비활성 사용자 작업 시도 예외"""
    pass 