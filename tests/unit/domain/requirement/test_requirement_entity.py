from dataclasses import replace
from datetime import datetime
from uuid import uuid4

import pytest

from resque_api.domain.project.entities import Project, ProjectMember
from resque_api.domain.requirement.entities import Requirement
from resque_api.domain.requirement.exceptions import (
    DependencyCycleError,
    InvalidStatusTransitionError,
    InvalidPriorityError,
    RequirementDependencyNotFoundError,
    RequirementTitleLengthError,
)
from resque_api.domain.requirement.value_objects import (
    RequirementDescription,
    RequirementPriority,
    RequirementTag,
    RequirementStatusEnum,
    RequirementTags,
    RequirementTitle,
)


class TestRequirementCreation:
    def test_create_valid_requirement(self, base_requirement):
        """요구사항 생성 검증 테스트"""
        requirement: Requirement = base_requirement
        assert requirement.title.value == "Base Requirement"
        assert requirement.status.value == RequirementStatusEnum.TODO
        assert requirement.priority.value == 1

    def test_create_with_invalid_title(self, valid_requirement_data):
        """유효하지 않은 제목으로 생성 시 예외 발생"""
        with pytest.raises(RequirementTitleLengthError) as excinfo:
            invalid_title = RequirementTitle("")
            Requirement(**{**valid_requirement_data, "title": invalid_title})


class TestRequirementStatusTransitions:
    def test_valid_status_transition(self, base_requirement: Requirement):
        """유효한 상태 변경 테스트"""
        current_status = base_requirement.status

        if current_status == RequirementStatusEnum.TODO:
            updated = base_requirement.change_status(RequirementStatusEnum.IN_PROGRESS)
            assert updated.status == RequirementStatusEnum.IN_PROGRESS
        elif current_status == RequirementStatusEnum.IN_PROGRESS:
            updated = base_requirement.change_status(RequirementStatusEnum.DONE)
            assert updated.status == RequirementStatusEnum.DONE

    def test_invalid_transition_from_done(self, base_requirement: Requirement):
        """DONE 상태에서 변경 시도"""
        if base_requirement.status == RequirementStatusEnum.DONE:
            with pytest.raises(InvalidStatusTransitionError):
                base_requirement.change_status(RequirementStatusEnum.TODO)


class TestRequirementPriority:
    @pytest.mark.parametrize("priority", [1, 2, 3])
    def test_set_valid_priority(self, base_requirement: Requirement, priority):
        """유효한 우선순위 설정 테스트"""
        updated = base_requirement.set_priority(priority)
        assert updated.priority.value == priority

    @pytest.mark.parametrize("priority", [0, 4])
    def test_invalid_priority_value(self, base_requirement, priority):
        """유효하지 않은 우선순위 값 테스트"""
        with pytest.raises(InvalidPriorityError):
            base_requirement.set_priority(priority)


class TestRequirementTags:
    def test_add_tags(self, base_requirement: Requirement):
        """태그 추가 테스트"""
        # "urgent"와 "backend" 태그 추가
        updated = base_requirement.add_tag("urgent").add_tag("backend")
        
        # 태그가 올바르게 추가되었는지 확인
        assert set(updated.tags.as_list()) == {RequirementTag.create("urgent"), RequirementTag.create("backend")}

    def test_remove_tag(self, base_requirement: Requirement):
        """태그 제거 테스트"""
        # "urgent"와 "backend" 태그를 추가
        updated = replace(base_requirement, tags=RequirementTags((RequirementTag.create("urgent"), RequirementTag.create("backend"))))
        
        # "urgent" 태그 제거
        updated = updated.remove_tag("urgent")
        
        # "urgent" 태그가 제거되었는지 확인
        assert RequirementTag.create("urgent") not in updated.tags
        # "backend" 태그는 여전히 존재해야 한다.
        assert RequirementTag.create("backend") in updated.tags


class TestRequirementComments:
    def test_add_comment(self, base_requirement: Requirement, sample_user):
        """코멘트 추가 테스트"""
        updated, comment = base_requirement.add_comment(sample_user, "Test comment")
        assert len(updated.comments) == 1
        assert updated.comments[comment.id].content == "Test comment"

    def test_edit_comment_content(self, base_requirement, sample_user):
        """코멘트 내용 수정 테스트"""
        updated, comment = base_requirement.add_comment(sample_user, "Initial content")
        edited_comment = comment.edit_content("Updated content")
        assert edited_comment.content == "Updated content"
        assert edited_comment.requirement_id == comment.requirement_id
        assert edited_comment.author_id == comment.author_id
        assert edited_comment.created_at == comment.created_at


class TestRequirementAssignee:
    def test_change_assignee(self, base_requirement: Requirement, another_member: ProjectMember):
        """담당자 변경 테스트"""
        updated = base_requirement.change_assignee(another_member)
        assert updated.assignee_id == another_member.id

    def test_no_change_if_same_assignee(self, base_requirement: Requirement, sample_member: ProjectMember):
        """동일한 담당자로 변경 시 변경 없음"""
        updated = base_requirement.change_assignee(sample_member)
        assert updated.assignee_id == base_requirement.assignee_id

    def test_unassign_assignee(self, base_requirement: Requirement):
        """담당자 해제 테스트"""
        updated = base_requirement.change_assignee(None)

        assert updated.assignee_id is None


class TestRequirementDependencies:
    def test_link_valid_predecessor(self, base_requirement):
        """유효한 선행 요구사항 연결"""
        another_requirement = Requirement(
            project_id=uuid4(),
            title=RequirementTitle("Another Requirement"),
            description=RequirementDescription("Another description"),
            assignee_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(1),
        )

        updated = base_requirement.link_predecessor(another_requirement)

        assert another_requirement.id in updated.dependencies
        assert len(updated.dependencies) == 1

    def test_prevent_duplicate_predecessor(self, base_requirement):
        """중복 선행 요구사항 연결 방지"""
        another_requirement = Requirement(
            project_id=uuid4(),
            title=RequirementTitle("Another Requirement"),
            description=RequirementDescription("Another description"),
            assignee_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(3),
        )

        updated = base_requirement.link_predecessor(another_requirement)
        updated_again = updated.link_predecessor(another_requirement)

        assert len(updated_again.dependencies) == 1

    def test_valid_dependency_chain(self, base_requirement):
        """유효한 다단계 의존성 체인"""
        req1 = Requirement(
            project_id=uuid4(),
            title=RequirementTitle("Requirement 1"),
            description=RequirementDescription("Description 1"),
            assignee_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(3),
        )

        req2 = req1.link_predecessor(
            Requirement(
                project_id=uuid4(),
                title=RequirementTitle("Requirement 2"),
                description=RequirementDescription("Description 2"),
                assignee_id=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                priority=RequirementPriority(2),
            )
        )

        req3 = req2.link_predecessor(
            Requirement(
                project_id=uuid4(),
                title=RequirementTitle("Requirement 3"),
                description=RequirementDescription("Description 3"),
                assignee_id=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                priority=RequirementPriority(1),
            )
        )

        updated = base_requirement.link_predecessor(req3)

        assert len(updated.dependencies) == 1
        assert req3.id in updated.dependencies

    def test_unlink_valid_predecessor(self, base_requirement):
        """유효한 선행 요구사항 제거"""
        another_requirement = Requirement(
            project_id=uuid4(),
            title=RequirementTitle("Another Requirement"),
            description=RequirementDescription("Another description"),
            assignee_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(1),
        )

        updated = base_requirement.link_predecessor(another_requirement)
        updated = updated.unlink_predecessor(another_requirement)

        assert another_requirement.id not in updated.dependencies
        assert len(updated.dependencies) == 0

    def test_unlink_nonexistent_predecessor(self, base_requirement):
        """존재하지 않는 선행 요구사항 제거 시 예외 발생"""
        another_requirement = Requirement(
            project_id=uuid4(),
            title=RequirementTitle("Nonexistent Requirement"),
            description=RequirementDescription("Nonexistent description"),
            assignee_id=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(1),
        )

        with pytest.raises(RequirementDependencyNotFoundError):
            base_requirement.unlink_predecessor(another_requirement)