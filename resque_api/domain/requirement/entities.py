from dataclasses import dataclass, field, replace
from datetime import datetime
from typing import Dict, List, Self
from uuid import UUID, uuid4

from resque_api.domain.base.entity import Entity
from resque_api.domain.project.entities import ProjectMember
from resque_api.domain.requirement.exceptions import (
    CommentEditPermissionError,
    CommentNotFoundError,
    DependencyCycleError,
    RequirementDependencyNotFoundError,
    RequirementTitleLengthError,
)
from resque_api.domain.requirement.value_objects import (
    RequirementTitle,
    RequirementDescription,
    RequirementPriority,
    RequirementStatus,
    RequirementTags,
)


@dataclass(frozen=True)
class RequirementComment(Entity):
    """요구사항 코멘트 엔티티"""
    requirement_id: UUID
    author_id: UUID
    content: str
    
    created_at: datetime = field(default_factory=datetime.utcnow)

    def edit_content(self, new_content: str) -> Self:
        """코멘트 내용 수정"""
        return replace(self, content=new_content)


@dataclass(frozen=True)
class Requirement(Entity):
    """요구사항 도메인 엔티티"""

    project_id: UUID
    title: RequirementTitle
    description: RequirementDescription
    assignee_id: UUID | None
    created_at: datetime
    updated_at: datetime
    priority: RequirementPriority

    status: RequirementStatus = field(default_factory=RequirementStatus)
    tags: RequirementTags = field(default_factory=RequirementTags)
    comments: Dict[UUID, RequirementComment] = field(default_factory=dict)
    dependencies: list[UUID] = field(default_factory=list)

    def change_status(self, new_status: RequirementStatus) -> Self:
        """요구사항 상태 변경"""
        
        return replace(self, status=self.status.change_status(new_status))

    def set_priority(self, priority: int) -> Self:
        """우선순위 설정"""

        return replace(self, priority=RequirementPriority(priority))

    def add_tag(self, tag: str) -> Self:
        """태그 추가"""

        return replace(self, tags=self.tags.add_tag(tag))

    def remove_tag(self, tag: str) -> Self:
        """태그 제거"""
    
        return replace(self, tags=self.tags.remove_tag(tag))

    def add_comment(
        self, author: ProjectMember, comment: str
    ) -> tuple[Self, RequirementComment]:
        """댓글 추가"""
        new_comment = RequirementComment(
            requirement_id=self.id,
            author_id=author.id,
            content=comment,
        )
        return (
            replace(self, comments={**self.comments, new_comment.id: new_comment}),
            new_comment,
        )

    def edit_comment(
        self, author: ProjectMember, comment_id: UUID, new_content: str
    ) -> tuple[Self, RequirementComment]:
        """댓글 수정"""
        comment = self.comments.get(comment_id)
        if not comment:
            raise CommentNotFoundError("수정하려는 댓글을 찾을 수 없습니다.")
        if comment.author_id != author.id:
            raise CommentEditPermissionError("댓글을 수정할 권한이 없습니다.")

        edited_comment = comment.edit_content(new_content)
        return (
            replace(self, comments={**self.comments, comment_id: edited_comment}),
            edited_comment,
        )

    def change_assignee(self, new_assignee: ProjectMember | None) -> Self:
        """담당자 변경"""
        new_assignee_id = new_assignee.id if new_assignee else None
        return self if self.assignee_id == new_assignee_id else replace(self, assignee_id=new_assignee_id)


    def link_predecessor(self, requirement: Self) -> Self:
        """선행 요구사항 연결"""
        if requirement.id in self.dependencies:
            return self

        return replace(
            self, dependencies=[*self.dependencies, requirement.id]
        )

    def unlink_predecessor(self, predecessor: Self) -> Self:
        """선행 요구사항 제거"""
        if predecessor.id not in self.dependencies:
            raise RequirementDependencyNotFoundError(
                "해당 선행 요구사항이 존재하지 않습니다."
            )

        return replace(
            self,
            dependencies=[req_id for req_id in self.dependencies if req_id != predecessor.id]
        )
