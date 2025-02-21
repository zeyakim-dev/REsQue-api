from dataclasses import dataclass, field, replace
from datetime import datetime
from uuid import UUID, uuid4
from typing import Dict, List, Optional, Self

from resque_api.domain.project.entities import ProjectMember
from resque_api.domain.requirement.value_objects import RequirementStatus, RequirementPriority
from resque_api.domain.requirement.exceptions import CommentEditPermissionError, CommentNotFoundError, RequirementDependencyNotFoundError, RequirementPriorityError, DependencyCycleError, RequirementTitleLengthError, TagNotFoundError 


@dataclass(frozen=True)
class RequirementComment:
    """요구사항 코멘트 엔티티"""
    requirement_id: UUID
    author_id: UUID
    content: str
    created_at: datetime

    id: UUID = field(default_factory=uuid4)

    def edit_content(self, new_content: str) -> Self:
        """코멘트 내용 수정"""
        return replace(self, content=new_content)


@dataclass(frozen=True)
class Requirement:
    """요구사항 도메인 엔티티"""
    
    project_id: UUID
    title: str
    description: str
    assignee: ProjectMember | None
    created_at: datetime
    updated_at: datetime
    priority: RequirementPriority

    id: UUID = field(default_factory=uuid4)
    status: RequirementStatus = field(default=RequirementStatus.TODO)
    tags: List[str] = field(default_factory=list)
    comments: Dict[UUID, RequirementComment] = field(default_factory=dict)
    dependencies: Dict[UUID, Self] = field(default_factory=dict)

    def __post_init__(self):
        """초기화 시 유효성 검증"""
        self._validate_title()

    def _validate_title(self):
        """제목 유효성 검사"""
        if len(self.title) > 100:
            raise RequirementTitleLengthError("제목은 100자 이내로 작성해야 합니다.")
        if len(self.title) < 2:
            raise RequirementTitleLengthError("제목은 2자 이상이어야 합니다.")

    def change_status(self, new_status: RequirementStatus) -> Self:
        """요구사항 상태 변경"""
        return replace(self, status=self.status.change_status(new_status))

    def set_priority(self, priority: int) -> Self:
        """우선순위 설정"""
        if not 1 <= priority <= 3:
            raise RequirementPriorityError("Priority must be between 1 and 3")
        return replace(self, priority=RequirementPriority(priority))

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
            raise TagNotFoundError (f"Tag '{normalized_tag}' does not exist.")
        return replace(self, tags=[t for t in self.tags if t != normalized_tag])

    def add_comment(self, author: ProjectMember, comment: str) -> tuple[Self, RequirementComment]:
        """댓글 추가"""
        new_comment = RequirementComment(
            requirement_id=self.id,
            author_id=author.id,
            content=comment,
            created_at=datetime.utcnow(),
        )
        return replace(self, comments={**self.comments, new_comment.id: new_comment}), new_comment

    def edit_comment(self, author: ProjectMember, comment_id: UUID, new_content: str) -> tuple[Self, RequirementComment]:
        """댓글 수정"""
        comment = self.comments.get(comment_id)
        if not comment:
            raise CommentNotFoundError("수정하려는 댓글을 찾을 수 없습니다.")
        if comment.author_id != author.id:
            raise CommentEditPermissionError("댓글을 수정할 권한이 없습니다.")

        edited_comment = comment.edit_content(new_content)
        return replace(self, comments={**self.comments, comment_id: edited_comment}), edited_comment
    
    def change_assignee(self, new_assignee: ProjectMember | None) -> Self:
        """담당자 변경"""
        if self.assignee == new_assignee:
            return self
        return replace(self, assignee=new_assignee)

    def link_predecessor(self, requirement: Self) -> Self:
        """선행 요구사항 연결"""
        if requirement.id in self.dependencies:
            return self

        if self.has_cycle(requirement):
            raise DependencyCycleError("Cyclic dependency detected.")

        return replace(self, dependencies={**self.dependencies, requirement.id: requirement})

    def has_cycle(self, new_requirement: Self) -> bool:
        """새 요구사항을 추가했을 때 순환 참조 발생 여부 확인 (DFS)"""
        def dfs(requirement: Self, path: set[UUID]) -> bool:
            if requirement.id in path:
                return True
            
            path.add(requirement.id)
            result = any(dfs(dep, path) for dep in requirement.dependencies.values())
            path.remove(requirement.id)
            return result

        return dfs(new_requirement, {self.id})

    def unlink_predecessor(self, requirement: Self) -> Self:
        """선행 요구사항 제거"""
        if requirement.id not in self.dependencies:
            raise RequirementDependencyNotFoundError("해당 선행 요구사항이 존재하지 않습니다.")

        return replace(self, dependencies={k: v for k, v in self.dependencies.items() if k != requirement.id})