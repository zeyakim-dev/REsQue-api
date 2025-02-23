import pytest
from uuid import uuid4
from datetime import datetime
from resque_api.domain.requirement.entities import Requirement
from resque_api.domain.requirement.value_objects import (
    RequirementTitle,
    RequirementDescription,
    RequirementPriority,
)
from resque_api.domain.project.entities import ProjectMember, Project


@pytest.fixture
def valid_requirement_data(project_with_sample_user: Project, sample_member: ProjectMember):
    """유효한 요구사항 데이터를 반환"""
    return {
        "project_id": project_with_sample_user.id,
        "title": RequirementTitle("Base Requirement"),
        "description": RequirementDescription("Base requirement description"),
        "assignee_id": sample_member.id,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "priority": RequirementPriority(1),
    }


@pytest.fixture
def base_requirement(valid_requirement_data):
    """기본 요구사항 객체 생성"""
    return Requirement(**valid_requirement_data)


@pytest.fixture
def requirement_1(valid_requirement_data):
    """선행 요구사항이 없는 요구사항 객체 생성"""
    data = {**valid_requirement_data, "title": RequirementTitle("Requirement 1"), "priority": RequirementPriority(1)}
    return Requirement(**data)

@pytest.fixture
def requirement_2(valid_requirement_data):
    """선행 요구사항이 없는 다른 요구사항 객체 생성"""
    data = {**valid_requirement_data, "title": RequirementTitle("Requirement 2"), "priority": RequirementPriority(2)}
    return Requirement(**data)

@pytest.fixture
def requirement_3(requirement_1: Requirement, requirement_2: Requirement, valid_requirement_data):
    """두 개의 요구사항을 의존성으로 연결한 요구사항 객체 생성"""
    data = {
        **valid_requirement_data,
        "title": RequirementTitle("Requirement 3"),
        "priority": RequirementPriority(3),
        "dependencies": [requirement_1.id, requirement_2.id]  # dependencies 수정
    }
    return Requirement(**data)

@pytest.fixture
def requirement_4(requirement_1: Requirement, valid_requirement_data):
    """Requirement 1을 선행 요구사항으로 가진 요구사항 객체 생성"""
    data = {
        **valid_requirement_data,
        "title": RequirementTitle("Requirement 4"),
        "priority": RequirementPriority(4),
        "dependencies": [requirement_1.id]  # dependencies 수정
    }
    return Requirement(**data)
