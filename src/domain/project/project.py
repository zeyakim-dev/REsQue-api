from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Protocol
from uuid import UUID

from src.domain.project.project_member import ProjectMember, Role
from src.domain.project.values import Title, Description, Status


@dataclass(frozen=True)
class Project:
    id: UUID
    title: Title
    description: Description
    founder_id: UUID
    status: Status
    created_at: datetime
    members: Dict[UUID, ProjectMember]

    @classmethod
    def reconstitute(
        cls,
        id: UUID,
        title: str,
        description: str,
        founder_id: UUID,
        status: str,
        created_at: datetime,
        members: Dict[UUID, ProjectMember] = None,
    ) -> "Project":
        """저장소에서 엔티티를 재구성할 때 사용하는 팩토리 메서드"""
        return cls(
            id=id,
            title=Title(title),
            description=Description(description),
            founder_id=founder_id,
            status=Status(status),
            created_at=created_at,
            members=members or {},
        )

    def update_status(self, new_status: Status) -> "Project":
        """프로젝트의 상태를 변경합니다"""
        transitioned_status = self.status.transition_to(new_status)

        return Project(
            id=self.id,
            title=self.title,
            description=self.description,
            founder_id=self.founder_id,
            status=transitioned_status,
            created_at=self.created_at,
            members=self.members,
        )

    def is_already_joined(self, user_id: UUID) -> bool:
        """사용자가 이미 프로젝트에 참여했는지 확인합니다"""
        return any(
            member.user_id == user_id 
            for member in self.members.values()
        )

    def _is_admin(self, user_id: UUID) -> bool:
        """해당 사용자가 프로젝트의 관리자인지 확인합니다"""
        return any(
            member.user_id == user_id and member.role == Role.ADMIN
            for member in self.members.values()
        )

    def add_member(
        self, new_member: ProjectMember
    ) -> "Project":
        """프로젝트에 새 멤버를 추가합니다"""
        if new_member.id in self.members:
            raise ValueError("이미 존재하는 멤버입니다")
        
        updated_members = {
            **self.members,
            new_member.id: new_member
        }

        return Project(
            id=self.id,
            title=self.title,
            description=self.description,
            founder_id=self.founder_id,
            status=self.status,
            created_at=self.created_at,
            members=updated_members,
        )

    def change_member_role(
        self, admin: ProjectMember, member: ProjectMember, new_role: Role
        ) -> "Project":
        """프로젝트 멤버의 역할을 변경합니다"""
        if admin.role is not Role.ADMIN:
            raise ValueError("관리자만 역할을 변경할 수 있습니다")

        # 멤버가 존재하는지 확인
        if member.id not in self.members:
            raise ValueError("프로젝트에 존재하지 않는 멤버입니다")

        # 새로운 멤버 객체 생성
        updated_member = member.change_role(new_role)
        
        # 새로운 members 딕셔너리 생성
        updated_members = {
            **self.members,
            member.id: updated_member
        }

        return Project(
            id=self.id,
            title=self.title,
            description=self.description,
            founder_id=self.founder_id,
            status=self.status,
            created_at=self.created_at,
            members=updated_members,
        )