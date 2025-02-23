from dataclasses import replace
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from resque_api.domain.project.entities import Project, ProjectMember
from resque_api.domain.project.value_objects import ProjectRole, ProjectStatus
from resque_api.domain.user.entities import User


@pytest.fixture
def valid_project_data():
    """유효한 프로젝트 데이터"""
    return {
        "title": "Test Project",
        "description": "A description for the test project",
        "status": ProjectStatus.ACTIVE,
        "owner_id": uuid4(),
        "created_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def valid_project(valid_project_data, valid_user):
    """유효한 프로젝트 객체 생성"""
    project_data = {**valid_project_data, "owner_id": valid_user.id}
    project = Project(**project_data)

    # 프로젝트 생성 후 기본 소유자(MANAGER) 추가
    new_member = ProjectMember(user_id=valid_user.id, role=ProjectRole.MANAGER)
    project = project.replace(members=[new_member])
    
    return project


@pytest.fixture
def expired_project_invitation(valid_project):
    """만료된 초대 생성"""
    # 유효한 초대 생성 후 만료 처리
    invite_email = "expired@example.com"
    updated_project, invitation = valid_project.invite_member(
        invite_email, ProjectRole.MEMBER
    )
    expired_invitation = invitation.replace(
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )
    
    return replace(valid_project, invitations={invitation.code: expired_invitation})


@pytest.fixture
def user_for_invitation():
    """초대에 사용할 사용자 객체 생성"""
    return User(
        id=uuid4(),
        email="new@example.com",
        auth_provider="EMAIL",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def user_for_already_accepted_invitation():
    """이미 수락된 초대 코드로 사용할 사용자 생성"""
    return User(
        id=uuid4(),
        email="accepted@example.com",
        auth_provider="EMAIL",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def valid_project_with_invitations(valid_project):
    """초대가 포함된 유효한 프로젝트 생성"""
    invite_email = "invite@example.com"
    updated_project, invitation = valid_project.invite_member(
        invite_email, ProjectRole.MEMBER
    )
    return updated_project, invitation