from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Protocol
from uuid import UUID

from src.domain.project.project_member import ProjectMember, Role


class Status(Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class IdGenerator(Protocol):
    def generate(self) -> UUID: ...


@dataclass(frozen=True)
class Project:
    id: UUID
    title: str
    description: str
    founder_id: UUID
    status: Status
    created_at: datetime

    @staticmethod
    def create(
        project_info: dict,
        founder_id: UUID,
        id_generator: IdGenerator,
    ) -> "Project":
        return Project(
            id=id_generator.generate(),
            title=project_info["title"],
            description=project_info["description"],
            founder_id=founder_id,
            status=Status.DRAFT,
            created_at=datetime.now(),
        )

    def update_status(self, new_status: Status) -> "Project":
        return Project(
            id=self.id,
            title=self.title,
            description=self.description,
            founder_id=self.founder_id,
            status=new_status,
            created_at=self.created_at,
        )
