import pytest
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from resque_api.domain.project.entities import Project
from resque_api.domain.project.value_objects import InvitationStatus, ProjectStatus, ProjectRole
from resque_api.domain.project.exceptions import AlreadyAcceptedInvitationError, ExpiredInvitationError, InvalidTitleError, DuplicateMemberError
from resque_api.domain.user.entities import User
from dataclasses import replace

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

class TestProjectInvitationAcceptance:
    """초대 수락 테스트"""
    
    def test_invite_acceptance(self, valid_project: Project, valid_user):
        """유효한 초대 코드 수락 테스트"""
        # Given
        invite_email = "new@example.com"
        invitation = valid_project.invite_member(invite_email, ProjectRole.MEMBER)
        
        new_user = User(
            id=uuid4(),
            email=invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc)
        )
        
        # When
        updated_project = valid_project.accept_invitation(invitation.code, new_user)
        
        # Then
        # 멤버가 추가되었는지 확인
        assert any(
            member.user == new_user and member.role == ProjectRole.MEMBER
            for member in updated_project.members
        )
        
        # 초대 상태가 ACCEPTED로 변경되었는지 확인
        assert any(
            invite.code == invitation.code and invite.status == InvitationStatus.ACCEPTED
            for invite in updated_project.invitations
        )
    
    def test_expired_invitation_acceptance(self, valid_project: Project):
        """만료된 초대 코드 수락 시도"""
        # Given
        invite_email = "expired@example.com"
        
        # 초대 생성 후 만료시키기
        invitation = valid_project.invite_member(invite_email, ProjectRole.MEMBER)
        
        # 초대 만료 상태로 직접 설정 (테스트를 위한 조작)
        expired_invitation = invitation._replace(
            expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )
        
        # 기존 초대를 만료된 초대로 교체 (테스트를 위해 invitations 리스트 직접 수정)
        project_with_expired_invite = replace(
            valid_project,
            invitations={invitation.code: expired_invitation}
        )
        
        # 초대 수락 시도할 사용자 생성
        new_user = User(
            id=uuid4(),
            email=invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc)
        )
        
        # When/Then
        with pytest.raises(ExpiredInvitationError) as exc_info:
            project_with_expired_invite.accept_invitation(expired_invitation.code, new_user)
        
        assert "Invitation has expired" in str(exc_info.value)
    
    def test_already_accepted_invitation(self, valid_project: Project):
        """이미 수락된 초대 코드로 재시도"""
        # Given
        invite_email = "accepted@example.com"
        invitation = valid_project.invite_member(invite_email, ProjectRole.MEMBER)
        
        # 첫 번째 사용자가 초대 수락
        first_user = User(
            id=uuid4(),
            email=invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc)
        )
        
        updated_project = valid_project.accept_invitation(invitation.code, first_user)
        
        # 두 번째 사용자가 동일한 코드로 수락 시도
        second_user = User(
            id=uuid4(),
            email="another_" + invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc)
        )
        
        # When/Then
        with pytest.raises(AlreadyAcceptedInvitationError) as exc_info:
            updated_project.accept_invitation(invitation.code, second_user)
        
        assert "Invitation has already been accepted" in str(exc_info.value)

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