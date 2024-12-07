from dataclasses import dataclass
from uuid import UUID, uuid4

import pytest
from sqlalchemy.exc import IntegrityError

from src.domain.entity import Entity
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import (
    SQLAlchemyRepository,
)


@dataclass(frozen=True)
class FakeEntity(Entity):
    id: UUID
    name: str


class FakeModel:
    def __init__(self, id: UUID, name: str):
        self.id = id
        self.name = name


class FakeRepository(SQLAlchemyRepository[FakeModel, FakeEntity]):
    def __init__(self, session):
        super().__init__(session, FakeModel)

    def _to_model(self, entity: FakeEntity) -> FakeModel:
        return FakeModel(id=entity.id, name=entity.name)

    def _to_domain(self, model: FakeModel) -> FakeEntity:
        return FakeEntity(id=model.id, name=model.name)


class TestSQLAlchemyRepository:
    @pytest.fixture
    def session(self, mocker):
        return mocker.Mock()

    @pytest.fixture
    def repository(self, session):
        return FakeRepository(session)

    @pytest.fixture
    def entity(self):
        return FakeEntity(id=uuid4(), name="test_entity")

    def test_add_entity_with_integrity_error(self, mocker, repository, session, entity):
        """엔티티 추가 실패 테스트"""
        # Arrange
        session.flush.side_effect = IntegrityError(None, None, None)

        # Act
        with pytest.raises(IntegrityError):
            repository.add(entity)

        # Assert
        # 먼저 호출 순서만 검증
        assert len(session.mock_calls) == 3
        assert session.mock_calls[0].match(mocker.call.add(mocker.ANY))
        assert session.mock_calls[1].match(mocker.call.flush())
        assert session.mock_calls[2].match(mocker.call.rollback())

        # 추가로 전달된 모델의 속성 검증
        added_model = session.add.call_args[0][0]
        assert added_model.id == entity.id
        assert added_model.name == entity.name

        # 추가로 전달된 모델의 속성 검증
        added_model = session.add.call_args[0][0]
        assert added_model.id == entity.id
        assert added_model.name == entity.name

    def test_get_entity(self, mocker, repository, session, entity):
        """엔티티 조회 테스트"""
        # Arrange
        model = FakeModel(id=entity.id, name=entity.name)

        # Mock 체인 생성
        query_chain = (
            session.query.return_value.filter_by.return_value.first.return_value
        ) = model

        # Act
        result = repository.get(entity.id)

        # Assert
        assert result == entity
        assert result in repository.seen
        session.query.assert_called_once_with(FakeModel)

    def test_get_nonexistent_entity(self, mocker, repository, session):
        """존재하지 않는 엔티티 조회 테스트"""
        # Arrange
        # Mock 체인 생성
        query_chain = (
            session.query.return_value.filter_by.return_value.first.return_value
        ) = None

        # Act
        result = repository.get(uuid4())

        # Assert
        assert result is None
