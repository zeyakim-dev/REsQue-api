from dataclasses import replace
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from resque_api.domain.project.entities import Project
from resque_api.domain.project.exceptions import (
    AlreadyAcceptedInvitationError,
    ExpiredInvitationError,
    InvalidTitleError,
)
from resque_api.domain.project.value_objects import (
    InvitationStatus,
    ProjectRole,
    ProjectStatus,
)
from resque_api.domain.user.entities import User


class TestProject:
    """Project 엔티티 관련 테스트

    도메인 규칙:
    - 프로젝트는 고유한 제목, 설명을 가짐.
    - 프로젝트는 상태(예: ACTIVE, ARCHIVED)와 소유자(Owner)를 가짐.
    - 프로젝트의 소유자는 반드시 MANAGER 역할로 프로젝트에 포함됨.
    - 프로젝트에 대한 초대 기능을 포함하고 있으며, 초대 코드에는 만료일과 상태가 있음.
    - 초대 수락 후, 사용자 상태는 변경되며, 이미 수락된 초대는 재사용할 수 없음.
    """

    class TestProjectCreation:
        """프로젝트 생성 테스트

        프로젝트 엔티티의 기본 생성 로직에 대한 테스트를 포함합니다. 
        주로 프로젝트 제목과 설명을 기반으로 생성하며, 생성된 프로젝트의 
        상태와 소유자가 적절히 설정되는지 확인합니다.
        """

        def test_create_project(self, valid_project_data, valid_user):
            """기본 프로젝트 생성 테스트

            시나리오:
            1. 유효한 데이터를 사용하여 프로젝트 생성
            2. 프로젝트가 정상적으로 생성되었는지 검증
            3. 소유자는 반드시 프로젝트 멤버로 포함되며, 
               역할은 반드시 MANAGER여야 함

            검증 사항:
            - 프로젝트 ID가 UUID 형식이어야 함
            - 프로젝트 제목, 설명, 상태가 정상적으로 설정되어야 함
            - 프로젝트의 소유자는 MANAGER 역할로 포함되어야 함
            """
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
            """잘못된 제목으로 프로젝트 생성 시도

            시나리오:
            1. 빈 제목 또는 제목 길이가 100자를 초과하는 경우
            2. InvalidTitleError가 발생하는지 검증
            """
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
        """프로젝트 멤버 관리 테스트

        프로젝트에 멤버를 추가하거나 제거하는 과정에서 발생할 수 있는 
        예외와 상태 변화를 검증합니다. 프로젝트의 멤버는 역할을 가질 수 있으며, 
        멤버 추가 및 역할 변경이 적절히 처리되는지 확인합니다.
        """

        # 추가적인 멤버 관리 테스트를 여기에 작성

class TestProjectInvitation:
    """프로젝트 초대 관련 테스트

    프로젝트 초대 기능에 대한 테스트로, 사용자를 초대하고 초대 상태를 
    수락/거절하는 과정에서 발생할 수 있는 예외와 흐름을 검증합니다.
    """

    def test_create_invitation(self, valid_project: Project):
        """초대 생성 테스트

        시나리오:
        1. 프로젝트에 새로운 멤버 초대
        2. 초대 이메일, 역할, 만료일 등의 정보가 정확히 설정되었는지 검증

        검증 사항:
        - 초대 이메일이 올바르게 설정되어야 함
        - 초대 상태가 예상대로 설정되어야 함
        - 만료일이 현재 시간과 7일 이내여야 함
        """
        # Given
        invite_email = "invite@example.com"

        # When
        updated_project, invitation = valid_project.invite_member(
            invite_email, ProjectRole.MEMBER
        )

        # Then
        assert invitation.email == invite_email
        assert invitation.role == ProjectRole.MEMBER
        assert invitation.expires_at > datetime.now(timezone.utc)
        assert invitation.expires_at < datetime.now(timezone.utc) + timedelta(days=8)
        assert any(
            invite.email == invite_email
            for code, invite in updated_project.invitations.items()
        )

    def test_invite_acceptance(self, valid_project: Project, valid_user):
        """초대 수락 테스트

        시나리오:
        1. 프로젝트에 초대된 사용자가 초대를 수락
        2. 사용자가 프로젝트 멤버로 추가되고, 초대 상태가 ACCEPTED로 변경되는지 검증
        """
        # Given
        invite_email = "new@example.com"
        updated_project, invitation = valid_project.invite_member(
            invite_email, ProjectRole.MEMBER
        )

        new_user = User(
            id=uuid4(),
            email=invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
        )

        # When
        updated_project, new_member = updated_project.accept_invitation(
            invitation.code, new_user
        )

        # Then
        assert any(
            member.user == new_user and member.role == ProjectRole.MEMBER
            for member in updated_project.members
        )

        # 초대 상태가 ACCEPTED로 변경되었는지 확인
        assert any(
            invitation.code == code and invite.status == InvitationStatus.ACCEPTED
            for code, invite in updated_project.invitations.items()
        )

    def test_expired_invitation_acceptance(self, valid_project: Project):
        """만료된 초대 코드 수락 시도

        시나리오:
        1. 만료된 초대 코드를 수락하려는 경우
        2. ExpiredInvitationError가 발생하는지 검증
        """
        # Given
        invite_email = "expired@example.com"
        updated_project, invitation = valid_project.invite_member(
            invite_email, ProjectRole.MEMBER
        )

        expired_invitation = replace(
            invitation, expires_at=datetime.now(timezone.utc) - timedelta(days=1)
        )

        project_with_expired_invite = replace(
            valid_project, invitations={invitation.code: expired_invitation}
        )

        new_user = User(
            id=uuid4(),
            email=invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
        )

        # When/Then
        with pytest.raises(ExpiredInvitationError) as exc_info:
            project_with_expired_invite.accept_invitation(
                expired_invitation.code, new_user
            )

        assert "Invitation has expired" in str(exc_info.value)

    def test_already_accepted_invitation(self, valid_project: Project):
        """이미 수락된 초대 코드로 재시도

        시나리오:
        1. 이미 수락된 초대 코드를 다시 사용하려는 경우
        2. AlreadyAcceptedInvitationError가 발생하는지 검증
        """
        # Given
        invite_email = "accepted@example.com"
        updated_project, invitation = valid_project.invite_member(
            invite_email, ProjectRole.MEMBER
        )

        first_user = User(
            id=uuid4(),
            email=invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
        )

        updated_project, first_member = updated_project.accept_invitation(
            invitation.code, first_user
        )

        second_user = User(
            id=uuid4(),
            email="another_" + invite_email,
            auth_provider="EMAIL",
            status="ACTIVE",
            created_at=datetime.now(timezone.utc),
        )

        # When/Then
        with pytest.raises(AlreadyAcceptedInvitationError) as exc_info:
            updated_project.accept_invitation(invitation.code, second_user)

class TestProjectStatus:
    """프로젝트 상태 관리 테스트

    프로젝트의 상태 변경(예: 보관 상태로 변경)을 관리하는 테스트입니다. 
    상태 변경 후, 상태에 맞는 권한을 제한하고 불변성을 확인합니다.
    """

    def test_archive_project(self, valid_project, valid_user):
        """프로젝트 보관 상태로 변경 테스트

        시나리오:
        1. 활성 상태인 프로젝트를 보관 상태로 변경
        2. 프로젝트의 상태가 ARCHIVED로 변경되고, 소유자가 프로젝트 수정 불가 상태가 되는지 검증
        """
        # When
        archived_project = valid_project.update_status(ProjectStatus.ARCHIVED)

        # Then
        assert archived_project.status == ProjectStatus.ARCHIVED
        assert not archived_project.can_modify(valid_user)
        assert archived_project != valid_project  # 불변성 검증
