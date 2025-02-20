from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import List, Self
from uuid import UUID
from resque_api.domain.project.value_objects import (
    InvitationStatus, ProjectStatus, ProjectRole, ProjectMember, ProjectInvitation
)
from resque_api.domain.project.exceptions import (
    InvalidTitleError, DuplicateMemberError, InvalidProjectStateError, DuplicateInvitationError, InvalidRoleError, InvalidInvitationCodeError
)
from resque_api.domain.user.entities import User
import secrets

@dataclass(frozen=True)
class Project:
    """프로젝트 엔티티"""
    id: UUID
    title: str
    description: str
    status: ProjectStatus
    owner: User
    created_at: datetime
    members: List[ProjectMember] = field(default_factory=list)
    invitations: dict[str, ProjectInvitation] = field(default_factory=dict)

    def __post_init__(self):
        """생성 시 유효성 검증"""
        self._validate_title()

        if not any(m.user == self.owner for m in self.members):
            new_member = ProjectMember(user=self.owner, role=ProjectRole.MANAGER)
            members = [new_member, *self.members]
            
            super().__setattr__('members', members)

    def _validate_title(self) -> None:
        """제목 유효성 검증"""
        if not self.title:
            raise InvalidTitleError("Title cannot be empty")
        if len(self.title) > 100:
            raise InvalidTitleError("Title is too long")

    def invite_member(self, email: str, role: ProjectRole) -> tuple[Self, 'ProjectInvitation']:
        """멤버 초대
        
        Args:
            email: 초대할 이메일
            role: 부여할 역할
        """
        if self.status == ProjectStatus.ARCHIVED:
            raise InvalidProjectStateError("Cannot invite to archived project")
        
        if email in {inv.email for inv in self.invitations.values()}:
            raise DuplicateInvitationError(f"{email} already invited")
        
        if role not in [ProjectRole.MEMBER, ProjectRole.VIEWER]:
            raise InvalidRoleError("Manager role cannot be invited")

        invitation = ProjectInvitation(
            email=email,
            role=role,
            expires_at=datetime.now(tz=self.created_at.tzinfo) + timedelta(days=7),
            status=InvitationStatus.PENDING,
            code=secrets.token_urlsafe(32)
        )

        if invitation.code in self.invitations:
            raise DuplicateInvitationError("Invitation code collision detected")
            
        new_invitations = {**self.invitations, invitation.code: invitation}
        return replace(self, invitations=new_invitations), invitation

    def accept_invitation(self, code: str, user: User) -> tuple[Self, 'ProjectMember']:
        invitation = self.invitations.get(code)
        if not invitation:
            raise InvalidInvitationCodeError("Invalid invitation code")
        
        if not invitation.email == user.email:
            # TODO New ERROR
            ...
        new_member = ProjectMember(
            user=user,
            role=invitation.role
        )

        updated_invitation = replace(invitation, status=InvitationStatus.ACCEPTED)
        new_invitations = {**self.invitations, code: updated_invitation}
        
        return replace(
            self,
            members=[*self.members, new_member],
            invitations=new_invitations
        ), new_member

    def can_modify(self, user: User) -> bool:
        """수정 권한 확인
        
        Args:
            user: 권한을 확인할 사용자
        """
        if self.status == ProjectStatus.ARCHIVED:
            return False

        member = next((m for m in self.members if m.user == user), None)
        if not member:
            return False

        return member.role in [ProjectRole.MANAGER, ProjectRole.MEMBER]

    def update_status(self, new_status: ProjectStatus) -> Self:
        """상태 변경
        
        Args:
            new_status: 새로운 상태
            
        Returns:
            새로운 Project 인스턴스
        """
        return Project(
            id=self.id,
            title=self.title,
            description=self.description,
            status=new_status,
            owner=self.owner,
            created_at=self.created_at,
            members=self.members
        ) 
    