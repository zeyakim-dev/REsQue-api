from uuid import UUID

import pytest
from sqlalchemy.orm import Mapped

from src.domain.user.user import User
from src.domain.user.values import HashedPassword, Username
from src.infrastructure.persistence.sqlalchemy.models.users import UserModel
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


class StubUserModel:
    """UserModel을 모방하는 단순한 스텁"""

    def __init__(self, id: UUID, username: str, hashed_password: str):
        self.id: UUID = id
        self.username: str = username
        self.hashed_password: str = hashed_password


class StubSession:
    def __init__(self):
        self.saved_models = {}
        self.committed = False

    def add(self, model):
        self.saved_models[model.id] = model

    def flush(self):
        self.committed = True

    def rollback(self):
        self.saved_models.clear()
        self.committed = False

    def query(self, model_class):
        return StubQuery(self.saved_models)

    def scalar(self, stmt):
        filters = {}
        column_name = stmt.whereclause.left.key
        value = stmt.whereclause.right.value
        filters[column_name] = value

        for model in self.saved_models.values():
            if all(getattr(model, key) == value for key, value in filters.items()):
                return 1
        return None


class StubQuery:
    def __init__(self, models):
        self.models = models
        self.filters = {}

    def filter_by(self, **kwargs):
        """filter_by 메서드를 흉내냅니다."""
        self.filters.update(kwargs)
        return self

    def first(self):
        """첫 번째 일치하는 결과를 반환합니다."""
        for model in self.models.values():
            matches = all(
                getattr(model, key) == value for key, value in self.filters.items()
            )
            if matches:
                return model
        return None

    def scalar(self):
        """scalar() 메서드를 흉내냅니다."""
        result = self.first()
        return 1 if result else None


class TestSQLAlchemyUserRepository:
    @pytest.fixture
    def user_data(self) -> dict:
        return {
            "id": UUID("12345678-1234-5678-1234-567812345678"),
            "username": "testuser",
            "hashed_password": "hashed_password_123",
        }

    @pytest.fixture
    def user_entity(self, user_data: dict) -> User:
        return User(id=user_data['id'],
                    username=Username(user_data['username']),
                    hashed_password=HashedPassword(user_data['hashed_password']))

    @pytest.fixture
    def stub_model(self, user_data: dict) -> StubUserModel:
        return StubUserModel(**user_data)

    @pytest.fixture
    def stub_session(self) -> StubSession:
        return StubSession()

    @pytest.fixture
    def repository(self, stub_session) -> SQLAlchemyUserRepository:
        return SQLAlchemyUserRepository(stub_session)

    def test_should_save_user_successfully(
        self,
        repository: SQLAlchemyUserRepository,
        stub_session: StubSession,
        user_entity: User,
    ):
        """사용자 저장이 성공적으로 수행되는지 테스트합니다."""
        # When
        repository.add(user_entity)

        # Then
        saved_model = stub_session.saved_models.get(user_entity.id)
        assert saved_model is not None
        assert saved_model.username == user_entity.username.value
        assert saved_model.hashed_password == user_entity.hashed_password.value
        assert stub_session.committed

    def test_should_find_user_by_id(
        self,
        repository: SQLAlchemyUserRepository,
        stub_session: StubSession,
        stub_model: StubUserModel,
    ):
        """ID로 사용자를 찾을 수 있는지 테스트합니다."""
        # Given
        stub_session.add(stub_model)

        # When
        found_user = repository.get(stub_model.id)

        # Then
        assert found_user is not None
        assert found_user.id == stub_model.id
        assert found_user.username.value == stub_model.username
        assert found_user.hashed_password.value == stub_model.hashed_password

    def test_should_find_user_by_username(
        self,
        repository: SQLAlchemyUserRepository,
        stub_session: StubSession,
        stub_model: StubUserModel,
    ):
        """사용자명으로 사용자를 찾을 수 있는지 테스트합니다."""
        # Given
        stub_session.add(stub_model)

        # When
        found_user = repository.find_by_username(stub_model.username)

        # Then
        assert found_user is not None
        assert found_user.username.value == stub_model.username

    def test_should_check_username_exists(
        self,
        repository: SQLAlchemyUserRepository,
        stub_session: StubSession,
        stub_model: StubUserModel,
    ):
        """사용자명 존재 여부를 확인할 수 있는지 테스트합니다."""
        # Given
        stub_session.add(stub_model)

        # When
        exists = repository.exists_by_username(stub_model.username)

        # Then
        assert exists is True
