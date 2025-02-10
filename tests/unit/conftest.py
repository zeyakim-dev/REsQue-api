import pytest
from datetime import datetime, timezone
from uuid import uuid4
from src.domain.user.value_objects import AuthProvider, UserStatus, Password
from src.infrastructure.security.password_hasher import BcryptPasswordHasher

@pytest.fixture
def hasher():
    """테스트용 해셔 인스턴스"""
    return BcryptPasswordHasher(rounds=4)

@pytest.fixture
def valid_user_data(hasher):
    """테스트용 사용자 데이터"""
    plain_password = "secure_password123"
    hashed_password = hasher.hash(plain_password)
    
    return {
        "id": uuid4(),
        "email": "test@example.com",
        "auth_provider": AuthProvider.EMAIL,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.now(timezone.utc),
        "password": Password(hashed_value=hashed_password)
    } 