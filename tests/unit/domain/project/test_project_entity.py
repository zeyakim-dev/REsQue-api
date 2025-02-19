import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from resque_api.domain.project.entities import Project
from resque_api.domain.project.value_objects import ProjectStatus, ProjectRole
from resque_api.domain.project.exceptions import InvalidTitleError, DuplicateMemberError
from resque_api.domain.user.entities import User

class TestProject:
    """Project 엔티티 테스트"""
    
    class TestProjectCreation:
        """프로젝트 생성 테스트"""
        
        def test_create_project(self, valid_project_data, valid_user):
            """기본 프로젝트 생성 테스트"""
            # When
            project = Project(**valid_project_data)
            
            # Then
            assert isinstance(project.id, UUID)
            assert project.title == valid_project_data["title"]
            assert project.description == valid_project_data["description"]
            assert project.status == ProjectStatus.ACTIVE
            assert project.owner == valid_user
            
            # owner가 manager로 멤버에 포함되어 있는지 확인
            assert any(
                member.user == valid_user and member.role == ProjectRole.MANAGER
                for member in project.members
            )
        
        def test_create_project_with_invalid_title(self, valid_project_data):
            """잘못된 제목으로 프로젝트 생성 시도"""
            # 빈 제목
            with pytest.raises(InvalidTitleError) as exc_info:
                Project(**{**valid_project_data, "title": ""})
            assert "Title cannot be empty" in str(exc_info.value)
            
            # 최대 길이 초과
            long_title = "a" * 101  # 100자 초과
            with pytest.raises(InvalidTitleError) as exc_info:
                Project(**{**valid_project_data, "title": long_title})
            assert "Title is too long" in str(exc_info.value)
    
    class TestProjectMemberManagement:
        """멤버 관리 테스트"""
        
        def test_add_member(self, valid_project, valid_user):
            """멤버 추가 테스트"""
            # Given
            new_member = User(
                id=uuid4(),
                email="member@example.com",
                auth_provider="EMAIL",
                status="ACTIVE",
                created_at=datetime.now(timezone.utc)
            )
            
            # When
            updated_project = valid_project.add_member(new_member, ProjectRole.MEMBER)
            
            # Then
            assert any(
                member.user == new_member and member.role == ProjectRole.MEMBER
                for member in updated_project.members
            )
        
        def test_add_duplicate_member(self, valid_project, valid_user):
            """중복 멤버 추가 시도"""
            # When/Then
            with pytest.raises(DuplicateMemberError):
                valid_project.add_member(valid_user, ProjectRole.MEMBER)

class TestProjectInvitationManagement:
    """초대 관리 테스트"""
    
    def test_create_invitation(self, valid_project: Project):
        """초대 생성 테스트"""
        # Given
        invite_email = "invite@example.com"
        
        # When
        invitation = valid_project.invite_member(invite_email, ProjectRole.MEMBER)
        
        # Then
        assert invitation.email == invite_email
        assert invitation.role == ProjectRole.MEMBER
        assert invitation.expires_at > datetime.now(timezone.utc)
        assert invitation.expires_at < datetime.now(timezone.utc) + timedelta(days=8)
        assert any(invite.email == invite_email for invite in valid_project.invitations)

class TestProjectPermissions:
    """권한 관리 테스트"""
    
    def test_can_modify(self, valid_project, valid_user):
        """수정 권한 확인 테스트"""
        # Given
        viewer = User(
            id=uuid4(),
            email="viewer@example.com",
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc)
        )
        project_with_viewer = valid_project.add_member(viewer, ProjectRole.VIEWER)
        
        # Then
        assert project_with_viewer.can_modify(valid_user)  # manager
        assert not project_with_viewer.can_modify(viewer)  # viewer
        
        # 비멤버
        non_member = User(
            id=uuid4(),
            email="non@example.com",
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc)
        )
        assert not project_with_viewer.can_modify(non_member)

class TestProjectStatus:
    """상태 관리 테스트"""
    
    def test_archive_project(self, valid_project, valid_user):
        """프로젝트 보관 테스트"""
        # When
        archived_project = valid_project.update_status(ProjectStatus.ARCHIVED)
        
        # Then
        assert archived_project.status == ProjectStatus.ARCHIVED
        assert not archived_project.can_modify(valid_user)
        assert archived_project != valid_project  # 불변성 검증 