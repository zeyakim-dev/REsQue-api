import dataclasses
from datetime import datetime
from uuid import UUID

import pytest

from src.domain.project.project_member import ProjectMember, Role


class StubIdGenerator:
    def __init__(self, fixed_uuid: str = "01937b5c-7757-7855-8138-355fc7d85155"):
        self._uuid = UUID(fixed_uuid)

    def generate(self) -> UUID:
        return self._uuid


class TestProjectMember:
    @pytest.fixture
    def id_generator(self):
        return StubIdGenerator()

    @pytest.fixture
    def user_id(self):
        return UUID("01937b64-4565-7865-8261-6d0cf7847b33")

    @pytest.fixture
    def project_id(self):
        return UUID("01937b64-4565-7865-8261-6d0cf7847b34")

    def test_create_project_member(
        self,
        user_id: UUID,
        project_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # When
        member = ProjectMember.create(
            user_id=user_id,
            project_id=project_id,
            role=Role.MEMBER,
            id_generator=id_generator,
        )

        # Then
        assert member.id == id_generator.generate()
        assert member.user_id == user_id
        assert member.project_id == project_id
        assert member.role == Role.MEMBER
        assert isinstance(member.joined_at, datetime)

    def test_project_member_is_immutable(
        self,
        user_id: UUID,
        project_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # Given
        member = ProjectMember.create(
            user_id=user_id,
            project_id=project_id,
            role=Role.MEMBER,
            id_generator=id_generator,
        )

        # When/Then
        with pytest.raises(dataclasses.FrozenInstanceError):
            member.role = Role.ADMIN

    def test_change_role(
        self,
        user_id: UUID,
        project_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # Given
        member = ProjectMember.create(
            user_id=user_id,
            project_id=project_id,
            role=Role.MEMBER,
            id_generator=id_generator,
        )

        # When
        updated_member = member.change_role(Role.MANAGER)

        # Then
        assert updated_member.role == Role.MANAGER
        assert updated_member.id == member.id
        assert updated_member.user_id == member.user_id
        assert updated_member.project_id == member.project_id
        assert updated_member.joined_at == member.joined_at
        assert member.role == Role.MEMBER  # 원본 객체는 변경되지 않음

    def test_create_project_member_with_different_id(
        self,
        user_id: UUID,
        project_id: UUID,
    ):
        # Given
        different_uuid = "01937b64-4565-7865-8261-6d0cf7847b35"
        different_id_generator = StubIdGenerator(different_uuid)

        # When
        member = ProjectMember.create(
            user_id=user_id,
            project_id=project_id,
            role=Role.MEMBER,
            id_generator=different_id_generator,
        )

        # Then
        assert member.id == UUID(different_uuid)

    def test_project_member_equality(
        self,
        user_id: UUID,
        project_id: UUID,
        id_generator: StubIdGenerator,
    ):
        # Given
        member1 = ProjectMember.create(
            user_id=user_id,
            project_id=project_id,
            role=Role.MEMBER,
            id_generator=id_generator,
        )
        member2 = ProjectMember.create(
            user_id=user_id,
            project_id=project_id,
            role=Role.MEMBER,
            id_generator=id_generator,
        )

        # Then
        assert member1 == member2