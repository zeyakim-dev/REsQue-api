from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID
from typing import List, Optional, Self

from resque_api.domain.project.entities import ProjectMember
from resque_api.domain.requirement.value_objects import RequirementStatus, RequirementPriority
from resque_api.domain.requirement.exceptions import RequirementPriorityError


@dataclass(frozen=True)
class RequirementComment:
    """요구사항 코멘트 엔티티"""
    requirement_id: UUID
    author_id: UUID
    content: str
    created_at: datetime

    def edit_content(self, new_content: str) -> Self:
        """코멘트 내용 수정"""
        return replace(self, content=new_content)


@dataclass(frozen=True)
class Requirement:
    """요구사항 도메인 엔티티"""
    id: UUID
    project_id: UUID
    title: str
    description: str
    status: RequirementStatus
    assignee_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    priority: RequirementPriority
    tags: List[str] = field(default_factory=list)
    comments: List[RequirementComment] = field(default_factory=list)
    dependencies: List[UUID] = field(default_factory=list)

    def change_status(self, new_status: RequirementStatus) -> Self:
        """요구사항 상태 변경"""
        return replace(self, status=self.status.change_status(new_status))

    def set_priority(self, priority: int) -> Self:
        """우선순위 설정"""
        if not 1 <= priority <= 3:
            raise RequirementPriorityError("Priority must be between 1 and 3")
        return replace(self, priority=priority)

    def add_tag(self, tag: str) -> Self:
        """태그 추가"""
        normalized_tag = tag.strip().lower()
        
        if normalized_tag in self.tags:
            return self

        return replace(self, tags=[*self.tags, normalized_tag])

    def remove_tag(self, tag: str) -> Self:
        """태그 제거"""
        normalized_tag = tag.strip().lower()
        if normalized_tag not in self.tags:
            raise ValueError(f"Tag '{normalized_tag}' does not exist.")
        return replace(self, tags=[t for t in self.tags if t != normalized_tag])

    def add_comment(self, author: ProjectMember, comment: str) -> tuple[Self, RequirementComment]:
        """댓글 추가"""
        new_comment = RequirementComment(
            requirement_id=self.id,
            author_id=author.id,
            content=comment,
            created_at=datetime.utcnow(),
        )
        return replace(self, comments=[*self.comments, new_comment]), new_comment

    def change_assignee(self, new_assignee: ProjectMember) -> Self:
        """담당자 변경"""
        if self.assignee_id == new_assignee.user.id:
            return self
        return replace(self, assignee_id=new_assignee.user.id)


    def link_predecessor(self, requirement: Self) -> Self:
        """선행 요구사항 연결"""
        if requirement.id in self.dependencies:
            return self
        return replace(self, dependencies=[*self.dependencies, requirement.id])
