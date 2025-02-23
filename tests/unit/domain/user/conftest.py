import pytest
from datetime import datetime, timezone
from uuid import uuid4
from resque_api.domain.common.value_objects import Email
from resque_api.domain.user.value_objects import AuthProvider, UserStatus, Password
from resque_api.domain.user.entities import User


@pytest.fixture
def oauth_user_data():
    """OAuth 사용자 데이터를 반환"""
    return {
        "id": uuid4(),
        "email": Email("user@gmail.com"),
        "auth_provider": AuthProvider.GOOGLE,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.now(timezone.utc),
        "password": None  # OAuth는 비밀번호가 없음
    }

@pytest.fixture
def inactive_user_data():
    """비활성 사용자 데이터를 반환"""
    return {
        "id": uuid4(),
        "email": Email("inactive_user@example.com"),
        "auth_provider": AuthProvider.EMAIL,
        "status": UserStatus.INACTIVE,
        "created_at": datetime.now(timezone.utc),
        "password": Password("validPassword123")
    }


@pytest.fixture
def invalid_email_user(invalid_email_user_data):
    """잘못된 이메일을 가진 사용자 객체 반환"""
    return User(**invalid_email_user_data)


@pytest.fixture
def oauth_user(oauth_user_data):
    """OAuth 사용자 객체 반환"""
    return User(**oauth_user_data)


@pytest.fixture
def inactive_user(inactive_user_data):
    """비활성 사용자 객체 반환"""
    return User(**inactive_user_data)
