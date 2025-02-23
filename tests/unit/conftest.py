from datetime import datetime, timezone

import pytest
from uuid import uuid4

from resque_api.domain.user.value_objects import AuthProvider, UserStatus, Password
from resque_api.domain.user.entities import User


@pytest.fixture
def valid_user_data():
    """유효한 사용자 데이터를 반환"""
    return {
        "id": uuid4(),
        "email": "user@example.com",
        "auth_provider": AuthProvider.EMAIL,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.now(timezone.utc),
        "password": Password("validPassword123")
    }


@pytest.fixture
def valid_user(valid_user_data):
    """유효한 사용자 객체 반환"""
    return User(**valid_user_data)
