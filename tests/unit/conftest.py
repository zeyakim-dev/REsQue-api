import pytest
from datetime import datetime, timezone
from uuid import uuid4
from src.domain.user.value_objects import AuthProvider, UserStatus, Password
from src.infrastructure.security.password_hasher import BcryptPasswordHasher
from src.domain.project.entities import Project
from src.domain.project.value_objects import ProjectStatus
from src.domain.user.entities import User

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

@pytest.fixture
def valid_user():
    """테스트용 사용자"""
    return User(
        id=uuid4(),
        email="owner@example.com",
        auth_provider="EMAIL",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def valid_project_data(valid_user):
    """테스트용 프로젝트 데이터"""
    return {
        "id": uuid4(),
        "title": "Test Project",
        "description": "Test project description",
        "status": ProjectStatus.ACTIVE,
        "owner": valid_user,
        "created_at": datetime.now(timezone.utc),
        "members": []
    }

@pytest.fixture
def valid_project(valid_project_data):
    """테스트용 프로젝트"""
    return Project(**valid_project_data) 