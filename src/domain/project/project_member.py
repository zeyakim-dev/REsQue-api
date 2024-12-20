# src/domain/project/project_member.py
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID


class Role(Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"


class IdGenerator(Protocol):
    def generate(self) -> UUID: ...


@dataclass(frozen=True)
class ProjectMember:
    id: UUID
    user_id: UUID
    project_id: UUID
    role: Role
    joined_at: datetime

    def change_role(self, new_role: Role) -> "ProjectMember":
        return ProjectMember(
            id=self.id,
            user_id=self.user_id,
            project_id=self.project_id,
            role=new_role,
            joined_at=self.joined_at,
        )
