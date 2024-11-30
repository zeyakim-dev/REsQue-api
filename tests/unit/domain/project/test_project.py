import dataclasses
from datetime import datetime
from uuid import UUID

import pytest

from src.domain.project.project import Project, Status


class StubIdGenerator:
    def __init__(self, fixed_uuid: str = "01937b5c-7757-7855-8138-355fc7d85155"):
        self._uuid = UUID(fixed_uuid)

    def generate(self) -> UUID:
        return self._uuid


class TestProject:
    @pytest.fixture
    def id_generator(self):
        return StubIdGenerator()

    @pytest.fixture
    def founder_id(self):
        return UUID("01937b64-4565-7865-8261-6d0cf7847b33")

    @pytest.fixture
    def valid_project_info(self):
        return {
            "title": "Test Project",
            "description": "This is a test project"
        }

    def test_create_project(
        self,
        valid_project_info,
        founder_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # When
        project = Project.create(
            project_info=valid_project_info,
            founder_id=founder_id,
            id_generator=id_generator,
        )

        # Then
        assert project.id == id_generator.generate()
        assert project.title == valid_project_info["title"]
        assert project.description == valid_project_info["description"]
        assert project.founder_id == founder_id
        assert project.status == Status.DRAFT
        assert isinstance(project.created_at, datetime)

    def test_project_is_immutable(
        self,
        valid_project_info,
        founder_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # Given
        project = Project.create(
            project_info=valid_project_info,
            founder_id=founder_id,
            id_generator=id_generator,
        )

        # When/Then
        with pytest.raises(dataclasses.FrozenInstanceError):
            project.title = "New Title"

    def test_update_status(
        self,
        valid_project_info,
        founder_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # Given
        project = Project.create(
            project_info=valid_project_info,
            founder_id=founder_id,
            id_generator=id_generator,
        )

        # When
        updated_project = project.update_status(Status.IN_PROGRESS)

        # Then
        assert updated_project.status == Status.IN_PROGRESS
        assert updated_project.id == project.id
        assert updated_project.title == project.title
        assert updated_project.description == project.description
        assert updated_project.founder_id == project.founder_id
        assert updated_project.created_at == project.created_at
        assert project.status == Status.DRAFT  # 원본 객체는 변경되지 않음

    def test_create_project_with_different_id(
        self,
        valid_project_info,
        founder_id: UUID,
    ):
        # Given
        different_uuid = "01937b64-4565-7865-8261-6d0cf7847b35"
        different_id_generator = StubIdGenerator(different_uuid)

        # When
        project = Project.create(
            project_info=valid_project_info,
            founder_id=founder_id,
            id_generator=different_id_generator,
        )

        # Then
        assert project.id == UUID(different_uuid)

    def test_project_equality(
        self,
        valid_project_info,
        founder_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # Given
        project1 = Project.create(
            project_info=valid_project_info,
            founder_id=founder_id,
            id_generator=id_generator,
        )
        project2 = Project.create(
            project_info=valid_project_info,
            founder_id=founder_id,
            id_generator=id_generator,
        )

        # Then
        assert project1 == project2