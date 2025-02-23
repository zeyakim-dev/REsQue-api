from dataclasses import replace
from datetime import datetime, timezone
import hashlib

import pytest
from uuid import uuid4

from resque_api.domain.common.value_objects import Email
from resque_api.domain.project.entities import Project, ProjectMember
from resque_api.domain.project.value_objects import ProjectRole, ProjectStatus
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
        "password": Password(hashlib.sha256("validPassword123".encode()).hexdigest())
    }


@pytest.fixture
def valid_user(valid_user_data):
    """유효한 사용자 객체 반환"""
    return User(**valid_user_data)


@pytest.fixture
def valid_project_data(valid_user):
    """유효한 프로젝트 데이터"""
    return {
        "title": "Test Project",
        "description": "A description for the test project",
        "status": ProjectStatus.ACTIVE,
        "owner_id": valid_user.id,
        "created_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def valid_project(valid_project_data):
    """유효한 프로젝트 객체 생성"""
    project = Project(**valid_project_data)

    # 프로젝트 생성 후 기본 소유자(MANAGER) 추가
    new_member = ProjectMember(user_id=valid_project_data["owner_id"], role=ProjectRole.MANAGER)
    project = replace(project, members=[new_member])
    
    return project

@pytest.fixture
def sample_user() -> User:
    """새로운 사용자 객체 반환"""
    sample_user_data = {
        "email": Email("sampleuser@example.com"),
        "auth_provider": AuthProvider.EMAIL,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.now(timezone.utc),
        "password": Password("samplePassword123")
    }
    return User(**sample_user_data)


@pytest.fixture
def project_with_sample_user(valid_project: Project, sample_user: User) -> Project:
    """새 사용자 포함된 프로젝트"""
    new_member = ProjectMember(user_id=sample_user.id, role=ProjectRole.MEMBER)
    updated_project = replace(valid_project, members=[*valid_project.members, new_member])
    return updated_project


@pytest.fixture
def sample_member(project_with_sample_user: Project, sample_user: User) -> ProjectMember:
    """새 사용자의 프로젝트 멤버 반환"""
    return [member for member in project_with_sample_user.members if member.user_id == sample_user.id][0]

@pytest.fixture
def another_member(project_with_sample_user: Project) -> ProjectMember:
    new_user_id = uuid4()
    new_member = ProjectMember(user_id=new_user_id, role=ProjectRole.MEMBER)
    updated_project = replace(project_with_sample_user, members=[*project_with_sample_user.members, new_member])
    return [member for member in updated_project.members if member.user_id == new_user_id][0]