from resque_api.application.ports.security import PasswordHasher
from resque_api.domain.user.entities import User


def authenticate_user(
    user: User, plain_password: str, password_hasher: PasswordHasher
) -> bool:
    """사용자 인증

    Args:
        user: 인증할 사용자
        plain_password: 평문 비밀번호
        password_hasher: 비밀번호 해시 처리기
    """
    if not user or not plain_password:
        return False

    if not user.can_authenticate():
        return False

    return password_hasher.verify(plain_password, user.password.value)
