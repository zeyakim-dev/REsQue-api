from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List
from uuid import UUID
from src.domain.project.value_objects import (
    ProjectStatus, ProjectRole, ProjectMember, ProjectInvitation
)
from src.domain.project.exceptions import (
    InvalidTitleError, DuplicateMemberError, InvalidProjectStateError
)
from src.domain.user.entities import User

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

    def __post_init__(self):
        """생성 시 유효성 검증"""
        self._validate_title()
        self._ensure_owner_is_manager()

    def _validate_title(self) -> None:
        """제목 유효성 검증"""
        if not self.title:
            raise InvalidTitleError("Title cannot be empty")
        if len(self.title) > 100:
            raise InvalidTitleError("Title is too long")

    def _ensure_owner_is_manager(self) -> None:
        """소유자를 manager 역할로 멤버에 추가"""
        if not any(m.user == self.owner for m in self.members):
            # frozen=True이므로 새 리스트 생성
            object.__setattr__(
                self, 
                'members', 
                [*self.members, ProjectMember(self.owner, ProjectRole.MANAGER)]
            )

    def add_member(self, user: User, role: ProjectRole) -> 'Project':
        """멤버 추가
        
        Args:
            user: 추가할 사용자
            role: 부여할 역할
            
        Returns:
            새로운 Project 인스턴스
        """
        if any(m.user == user for m in self.members):
            raise DuplicateMemberError(f"User {user.email} is already a member")

        if self.status == ProjectStatus.ARCHIVED:
            raise InvalidProjectStateError("Cannot modify archived project")

        return Project(
            id=self.id,
            title=self.title,
            description=self.description,
            status=self.status,
            owner=self.owner,
            created_at=self.created_at,
            members=[*self.members, ProjectMember(user, role)]
        )

    def invite_member(self, email: str, role: ProjectRole) -> ProjectInvitation:
        """멤버 초대
        
        Args:
            email: 초대할 이메일
            role: 부여할 역할
        """
        if self.status == ProjectStatus.ARCHIVED:
            raise InvalidProjectStateError("Cannot invite to archived project")

        return ProjectInvitation(
            email=email,
            role=role,
            expires_at=datetime.now(tz=self.created_at.tzinfo) + timedelta(days=7)
        )

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

    def update_status(self, new_status: ProjectStatus) -> 'Project':
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