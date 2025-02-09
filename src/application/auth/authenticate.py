from src.domain.user.value_objects import Password
from src.domain.user.entities import User
from src.application.ports.security import PasswordHasher

def authenticate_user(user: User, plain_password: str, password_hasher: PasswordHasher) -> bool:
    """사용자 인증
    
    Args:
        user: 인증할 사용자
        plain_password: 평문 비밀번호
        password_hasher: 비밀번호 해시 처리기
    """
    if not user or not plain_password:
        return False
        
    hashed = password_hasher.hash(plain_password)
    password = Password(hashed_value=hashed)
    return user.authenticate(password)