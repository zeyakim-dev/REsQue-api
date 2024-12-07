from dataclasses import dataclass
from typing import Dict, Optional, Type
from uuid import UUID

import pytest

from src.application.commands.auth.register_command import RegisterCommand
from src.application.ports.repositories.repository import Repository
from src.application.ports.repositories.user.user_repository import UserRepository
from src.application.ports.uow import UnitOfWork
from src.domain.user.user import User


@dataclass
class StubPasswordHasher:
    """비밀번호 해싱을 단순화한 스텁"""

    def hash(self, password: str) -> str:
        return f"hashed_{password}"


@dataclass
class StubIdGenerator:
    """고정된 UUID를 반환하는 스텁"""

    fixed_id: UUID = UUID("12345678-1234-5678-1234-567812345678")

    def generate(self) -> UUID:
        return self.fixed_id


class StubUserRepository(UserRepository):
    """메모리 기반의 사용자 저장소 스텁"""

    def __init__(self):
        super().__init__()
        self._users: Dict[str, User] = {}

    def _add(self, user: User):
        if not self.exists_by_username(user.username):
            self._users[user.username] = user

    def _get(self, id: UUID):
        pass

    def find_by_username(self, username):
        return self._users[username]

    def exists_by_username(self, username: str) -> bool:
        return username in self._users


class StubUnitOfWork(UnitOfWork):
    """단순한 UnitOfWork 스텁"""

    def __init__(self):
        self._repositories = {UserRepository: StubUserRepository()}
        self.committed = False

    def get_repository(self, repository_type: Type[Repository]) -> Repository:
        return self._repositories[repository_type]

    def _commit(self) -> None:
        self.committed = True

    def _rollback(self) -> None:
        self.committed = False


class TestRegisterCommand:
    """RegisterCommand에 대한 테스트입니다."""

    @pytest.fixture
    def command(self, stub_password_hasher, stub_id_generator) -> RegisterCommand:
        return RegisterCommand(
            username="testuser",
            password="password123",
            _password_hasher=stub_password_hasher,
            _id_generator=stub_id_generator,
        )

    @pytest.fixture
    def stub_uow(self) -> StubUnitOfWork:
        return StubUnitOfWork()

    @pytest.fixture
    def stub_password_hasher(self) -> StubPasswordHasher:
        return StubPasswordHasher()

    @pytest.fixture
    def stub_id_generator(self) -> StubIdGenerator:
        return StubIdGenerator()

    def test_should_register_new_user_successfully(
        self, command: RegisterCommand, stub_uow: StubUnitOfWork
    ) -> None:
        """신규 사용자 등록이 성공적으로 완료되는지 테스트합니다."""
        # Act
        result = command.execute(stub_uow)

        # Assert
        assert isinstance(result, UUID)
        assert result == command._id_generator.fixed_id
        assert stub_uow.committed

    def test_should_prevent_duplicate_username_registration(
        self, command: RegisterCommand, stub_uow: StubUnitOfWork
    ) -> None:
        """중복된 사용자명으로 등록을 시도할 경우 예외가 발생하는지 테스트합니다."""
        # Arrange
        user_repo = stub_uow.get_repository(UserRepository)
        existing_user = User(
            id=UUID("00000000-0000-0000-0000-000000000000"),
            username="testuser",
            hashed_password="existing_hash",
        )
        user_repo.add(existing_user)

        # Act & Assert
        with pytest.raises(ValueError, match="이미 존재하는 사용자명입니다"):
            command.execute(stub_uow)

        assert not stub_uow.committed

    def test_should_handle_database_error_during_registration(
        self,
        command: RegisterCommand,
        stub_uow: StubUnitOfWork,
    ) -> None:
        """데이터베이스 오류 발생 시 트랜잭션이 롤백되는지 테스트합니다."""

        # Arrange
        class FailingUserRepository(StubUserRepository):
            def add(self, user: User) -> None:
                raise Exception("데이터베이스 오류")

        stub_uow._repositories[UserRepository] = FailingUserRepository()

        # Act & Assert
        with pytest.raises(Exception, match="데이터베이스 오류"):
            command.execute(stub_uow)

        assert not stub_uow.committed
