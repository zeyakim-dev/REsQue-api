import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from typing import Generator, Any
from resque_api.domain.requirement.value_objects import RequirementStatus
from resque_api.domain.user.value_objects import AuthProvider, UserStatus, Password
from resque_api.infrastructure.security.password_hasher import BcryptPasswordHasher
from resque_api.domain.project.entities import Project, ProjectMember
from resque_api.domain.project.value_objects import ProjectRole, ProjectStatus
from resque_api.domain.user.entities import User
from resque_api.domain.requirement.entities import Requirement, RequirementComment

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
        "members": [],
        "invitations": {}
    }

@pytest.fixture
def valid_project(valid_project_data) -> Project:
    """테스트용 프로젝트"""
    return Project(**valid_project_data)

@pytest.fixture(scope="module")
def sample_user() -> Generator[User, None, None]:
    """모듈 단위 재사용 사용자"""
    yield User(
        id=uuid4(),
        email="testuser@example.com",
        auth_provider="EMAIL",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )

@pytest.fixture
def project_with_member(sample_user: User) -> Project:
    """멤버가 포함된 프로젝트"""
    member = ProjectMember(
        user=sample_user,
        role="MEMBER"
    )
    return Project(
        id=uuid4(),
        title="Test Project",
        description="Test Description",
        status="ACTIVE",
        owner=sample_user,
        created_at=datetime.now(timezone.utc),
        members=[member],
        invitations={}
    )

@pytest.fixture(params=[1, 2, 3])
def valid_priority(request) -> int:
    """유효한 우선순위 값 (1-3)"""
    return request.param

@pytest.fixture(params=[0, 4])
def invalid_priority(request) -> int:
    """잘못된 우선순위 값"""
    return request.param

@pytest.fixture
def assignee(valid_user: User) -> ProjectMember:
    return ProjectMember(
        user=valid_user,
        role=ProjectRole.MANAGER
    )

@pytest.fixture
def base_requirement(project_with_member: Project, assignee: ProjectMember) -> Requirement:
    """기본 요구사항 템플릿"""
    return Requirement(
        project_id=project_with_member.id,
        title="Sample Requirement",
        description="Initial Description",
        assignee=assignee,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        priority=2,
        tags=[],
        comments=[],
        dependencies=[]
    )

@pytest.fixture
def sample_requirement(base_requirement: Requirement) -> Requirement:
    """일반적인 요구사항 인스턴스"""
    return base_requirement

@pytest.fixture
def requirement_with_tags(base_requirement: Requirement) -> Requirement:
    """태그가 포함된 요구사항"""
    return base_requirement.add_tag("backend").add_tag("urgent")

@pytest.fixture
def requirement_with_comments(base_requirement: Requirement, sample_user: User) -> Requirement:
    """코멘트가 포함된 요구사항"""
    return base_requirement.add_comment(sample_user, "First comment").add_comment(sample_user, "Second comment")

@pytest.fixture(params=[RequirementStatus.TODO, RequirementStatus.IN_PROGRESS, RequirementStatus.DONE])
def requirement_by_status(request: Any, base_requirement: Requirement) -> Requirement:
    """다양한 상태의 요구사항 생성"""
    return Requirement(
        project_id=base_requirement.project_id,
        title=base_requirement.title,
        description=base_requirement.description,
        assignee=assignee,
        status=request.param,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        priority=2,
        tags=base_requirement.tags,
        comments=base_requirement.comments,
        dependencies=base_requirement.dependencies,
    )

@pytest.fixture
def new_assignee():
    """새로운 담당자(ProjectMember) 생성 픽스처"""
    user = User(
        id=uuid4(),
        email="new_assignee@example.com",
        auth_provider="EMAIL",
        status="ACTIVE",
        created_at=datetime.now(timezone.utc)
    )

    return ProjectMember(
        user=user,
        role="developer",
    )


@pytest.fixture
def sample_comment(sample_user: User) -> RequirementComment:
    """테스트용 코멘트 인스턴스"""
    return RequirementComment(
        id=uuid4(),
        requirement_id=uuid4(),
        author_id=sample_user.id,
        content="Sample comment",
        created_at=datetime.now(timezone.utc)
    ) 