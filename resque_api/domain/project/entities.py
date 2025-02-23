import secrets
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from typing import Dict, List, Self
from uuid import UUID, uuid4

from resque_api.domain.base.aggregate import Aggregate
from resque_api.domain.base.entity import Entity
from resque_api.domain.project.exceptions import (
    AlreadyAcceptedInvitationError,
    DuplicateInvitationError,
    ExpiredInvitationError,
    InvalidInvitationCodeError,
    InvalidProjectStateError,
    InvalidRoleError,
)
from resque_api.domain.project.value_objects import (
    InvitationStatus,
    ProjectRole,
    ProjectStatus,
    ProjectTitle,
    InvitationCode,
    InvitationExpiration,
)
from resque_api.domain.user.entities import User
from resque_api.domain.common.value_objects import Email


@dataclass(frozen=True)
class ProjectMember(Entity):
    """프로젝트 멤버 엔티티"""

    user: User
    role: ProjectRole


@dataclass(frozen=True)
class ProjectInvitation(Entity):
    """프로젝트 초대 엔티티"""

    email: Email
    role: ProjectRole
    expires_at: InvitationExpiration = field(default_factory=lambda: InvitationExpiration.create(days=7))
    code: InvitationCode = field(default_factory=InvitationCode.generate)
    status: InvitationStatus = InvitationStatus.PENDING


@dataclass(frozen=True)
class Project(Aggregate):
    """프로젝트 엔티티 (Aggregate Root)"""

    title: ProjectTitle
    description: str
    status: ProjectStatus
    owner: User
    created_at: datetime
    members: List[ProjectMember] = field(default_factory=list)
    invitations: Dict[str, ProjectInvitation] = field(default_factory=dict)

    def __post_init__(self):
        if not any(m.user == self.owner for m in self.members):
            new_member = ProjectMember(user=self.owner, role=ProjectRole.MANAGER)
            super().__setattr__("members", [new_member, *self.members])

    def invite_member(self, email: Email, role: ProjectRole) -> tuple[Self, ProjectInvitation]:
        if self.status == ProjectStatus.ARCHIVED:
            raise InvalidProjectStateError("Cannot invite to archived project")

        if email.value in {inv.email.value for inv in self.invitations.values()}:
            raise DuplicateInvitationError(f"{email.value} already invited")

        if role not in [ProjectRole.MEMBER, ProjectRole.VIEWER]:
            raise InvalidRoleError("Manager role cannot be invited")

        invitation = ProjectInvitation(email=email, role=role)

        new_invitations = {**self.invitations, str(invitation.code): invitation}
        return replace(self, invitations=new_invitations), invitation

    def accept_invitation(self, code: str, user: User) -> tuple[Self, ProjectMember]:
        invitation = self.invitations.get(code)
        if not invitation:
            raise InvalidInvitationCodeError("Invalid invitation code")
        
        if invitation.expires_at.is_expired():
            raise ExpiredInvitationError("Invitation has expired")
        
        if invitation.status == InvitationStatus.ACCEPTED or any(m.user == user for m in self.members):
            raise AlreadyAcceptedInvitationError("User is already a project member")

        
        if invitation.email.value != user.email.value:
            raise InvalidInvitationCodeError(
                f"Invitation was sent to {invitation.email.value}, not {user.email.value}"
            )
        
        new_member = ProjectMember(user=user, role=invitation.role)
        updated_invitation = replace(invitation, status=InvitationStatus.ACCEPTED)
        new_invitations = {**self.invitations, str(invitation.code): updated_invitation}

        return replace(self, members=[*self.members, new_member], invitations=new_invitations), new_member

    def can_modify(self, user: User) -> bool:
        if self.status in [ProjectStatus.ARCHIVED, ProjectStatus.CLOSED]:
            return False
        
        member = next((m for m in self.members if m.user == user), None)
        return member is not None and member.role in [ProjectRole.MANAGER, ProjectRole.MEMBER]

    def update_status(self, new_status: ProjectStatus) -> Self:
        return replace(self, status=new_status)
