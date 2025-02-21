from datetime import datetime
from uuid import uuid4
import pytest
from resque_api.domain.requirement.entities import Requirement
from resque_api.domain.requirement.value_objects import RequirementPriority, RequirementStatus
from resque_api.domain.requirement.exceptions import (
    InvalidStatusTransitionError,
    RequirementPriorityError,
    RequirementTitleLengthError,
    DependencyCycleError
)
from resque_api.domain.project.entities import ProjectMember

class TestRequirementCreation:
    def test_create_valid_requirement(self, base_requirement):
        """요구사항 생성 검증 테스트"""
        requirement: Requirement = base_requirement
        assert requirement.title == "Sample Requirement"
        assert requirement.status == RequirementStatus.TODO
        assert requirement.priority == 2

    def test_create_with_invalid_title(self, project_with_member):
        """유효하지 않은 제목으로 생성 시 예외 발생"""
        with pytest.raises(RequirementTitleLengthError) as excinfo:
            Requirement(
                id=project_with_member.id,
                project_id=project_with_member.id,
                title="",  # Invalid empty title
                description="Test",
                status=RequirementStatus.TODO,
                assignee=None,
                created_at=project_with_member.created_at,
                updated_at=project_with_member.created_at,
                priority=1,
                tags=[],
                comments=[],
                dependencies=[]
            )

class TestRequirementStatusTransitions:
    def test_valid_status_transition(self, requirement_by_status):
        """유효한 상태 변경 테스트"""
        current_status = requirement_by_status.status

        if current_status == RequirementStatus.TODO:
            updated = requirement_by_status.change_status(RequirementStatus.IN_PROGRESS)
            assert updated.status == RequirementStatus.IN_PROGRESS
        elif current_status == RequirementStatus.IN_PROGRESS:
            updated = requirement_by_status.change_status(RequirementStatus.DONE)
            assert updated.status == RequirementStatus.DONE

    def test_invalid_transition_from_done(self, requirement_by_status):
        """DONE 상태에서 변경 시도"""
        if requirement_by_status.status == RequirementStatus.DONE:
            with pytest.raises(InvalidStatusTransitionError):
                requirement_by_status.change_status(RequirementStatus.TODO)

class TestRequirementPriority:
    @pytest.mark.parametrize("priority", [1, 2, 3])
    def test_set_valid_priority(self, base_requirement, priority):
        """유효한 우선순위 설정 테스트"""
        updated = base_requirement.set_priority(priority)
        assert updated.priority == priority

    @pytest.mark.parametrize("priority", [0, 4])
    def test_invalid_priority_value(self, base_requirement, priority):
        """유효하지 않은 우선순위 값 테스트"""
        with pytest.raises(RequirementPriorityError):
            base_requirement.set_priority(priority)

class TestRequirementTags:
    def test_add_and_remove_tags(self, base_requirement):
        """태그 추가 및 제거 테스트"""
        updated = base_requirement.add_tag("urgent").add_tag("backend")
        assert set(updated.tags) == {"urgent", "backend"}

        updated = updated.remove_tag("urgent")
        assert "urgent" not in updated.tags

class TestRequirementComments:
    def test_add_comment(self, base_requirement, sample_user):
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
    def test_change_assignee(self, base_requirement, new_assignee: ProjectMember):
        """담당자 변경 테스트"""
        updated = base_requirement.change_assignee(new_assignee)
        assert updated.assignee == new_assignee

    def test_no_change_if_same_assignee(self, base_requirement: Requirement):
        """동일한 담당자로 변경 시 변경 없음"""
        assignee = base_requirement.assignee
        updated = base_requirement.change_assignee(assignee)
        assert updated == base_requirement

    def test_unassign_assignee(self, base_requirement, new_assignee):
        """담당자 해제 테스트"""
        updated = base_requirement.change_assignee(new_assignee)
        updated = updated.change_assignee(None)

        assert updated.assignee is None


class TestRequirementDependencies:
    def test_link_valid_predecessor(self, base_requirement):
        """유효한 선행 요구사항 연결"""
        another_requirement = Requirement(
            project_id=uuid4(),
            title="Another Requirement",
            description="Another description",
            assignee=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(1)
        )

        updated = base_requirement.link_predecessor(another_requirement)

        assert another_requirement.id in updated.dependencies
        assert len(updated.dependencies) == 1

    def test_prevent_duplicate_predecessor(self, base_requirement):
        """중복 선행 요구사항 연결 방지"""
        another_requirement = Requirement(
            project_id=uuid4(),
            title="Another Requirement",
            description="Another description",
            assignee=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(3)
        )

        updated = base_requirement.link_predecessor(another_requirement)
        updated_again = updated.link_predecessor(another_requirement)

        assert len(updated_again.dependencies) == 1

    def test_detect_immediate_cycle(self, base_requirement):
        """직접 순환 참조 감지"""
        with pytest.raises(DependencyCycleError):
            base_requirement.link_predecessor(base_requirement)

    def test_detect_indirect_cycle(self, base_requirement):
        """간접 순환 참조 감지"""
        req_b = Requirement(
            project_id=uuid4(),
            title="Requirement B",
            description="Description B",
            assignee=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(2)
        )

        req_c = Requirement(
            project_id=uuid4(),
            title="Requirement C",
            description="Description C",
            assignee=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(1)
        )

        req_b = base_requirement.link_predecessor(req_b)
        req_c = req_b.link_predecessor(req_c)

        with pytest.raises(DependencyCycleError) as excinfo:
            req_c.link_predecessor(base_requirement)

        assert "Cyclic dependency" in str(excinfo.value)

    def test_valid_dependency_chain(self, base_requirement):
        """유효한 다단계 의존성 체인"""
        req1 = Requirement(
            project_id=uuid4(),
            title="Requirement 1",
            description="Description 1",
            assignee=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(3)
        )

        req2 = req1.link_predecessor(
            Requirement(
                project_id=uuid4(),
                title="Requirement 2",
                description="Description 2",
                assignee=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                priority=RequirementPriority(2)
            )
        )

        req3 = req2.link_predecessor(
            Requirement(
                project_id=uuid4(),
                title="Requirement 3",
                description="Description 3",
                assignee=None,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                priority=RequirementPriority(1)
            )
        )

        updated = base_requirement.link_predecessor(req3)

        assert len(updated.dependencies) == 1
        assert req3.id in updated.dependencies

    def test_unlink_valid_predecessor(self, base_requirement):
        """유효한 선행 요구사항 제거"""
        another_requirement = Requirement(
            project_id=uuid4(),
            title="Another Requirement",
            description="Another description",
            assignee=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            priority=RequirementPriority(1)
        )

        updated = base_requirement.link_predecessor(another_requirement)
        updated = updated.unlink_predecessor(another_requirement)

        assert another_requirement.id not in updated.dependencies
        assert len(updated.dependencies) == 0
