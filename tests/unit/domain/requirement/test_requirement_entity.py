import pytest
from resque_api.domain.requirement.entities import Requirement
from resque_api.domain.requirement.value_objects import RequirementStatus
from resque_api.domain.requirement.exceptions import (
    InvalidStatusTransitionError,
    RequirementPriorityError
)

class TestRequirementCreation:
    def test_create_valid_requirement(self, base_requirement):
        """요구사항 생성 검증 테스트"""
        requirement = base_requirement
        assert requirement.title == "Sample Requirement"
        assert requirement.status == RequirementStatus.TODO
        assert requirement.priority == 2

    def test_create_with_invalid_title(self, project_with_member):
        """유효하지 않은 제목으로 생성 시 예외 발생"""
        with pytest.raises(ValueError) as excinfo:
            Requirement(
                id=project_with_member.id,
                project_id=project_with_member.id,
                title="",  # Invalid empty title
                description="Test",
                status=RequirementStatus.TODO,
                assignee_id=None,
                created_at=project_with_member.created_at,
                updated_at=project_with_member.created_at,
                priority=1,
                tags=[],
                comments=[],
                dependencies=[]
            )
            
        assert "Title cannot be empty" in str(excinfo.value)

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
        updated = base_requirement.add_comment(sample_user, "Test comment")
        assert len(updated.comments) == 1
        assert updated.comments[0].content == "Test comment"

@pytest.mark.integration
class TestRequirementDependencies:
    def test_link_predecessors(self, base_requirement):
        """선행 요구사항 연결 테스트"""
        predecessor_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"
        updated = base_requirement.link_predecessor(predecessor_id)
        assert predecessor_id in updated.dependencies 