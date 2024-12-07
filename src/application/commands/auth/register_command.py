from dataclasses import dataclass
from typing import Optional
from uuid import UUID

from src.application.commands.command import Command
from src.application.ports.repositories.user.user_repository import UserRepository
from src.application.ports.uow import UnitOfWork
from src.domain.user.user import User
from src.domain.user.values import HashedPassword, Password, Username
from src.infrastructure.id.uuid_generator import UUIDv7Generator
from src.infrastructure.security.password_hasher import PasswordHasher


@dataclass(frozen=True)
class RegisterCommand(Command[UUID]):
    """새로운 사용자를 등록하는 커맨드입니다."""

    username: str
    password: str
    _password_hasher: PasswordHasher
    _id_generator: UUIDv7Generator

    def execute(self, uow: UnitOfWork) -> UUID:
        """사용자 등록을 수행합니다.

        트랜잭션 범위 내에서 사용자 생성과 저장을 수행하며,
        모든 데이터베이스 작업이 원자적으로 처리됩니다.

        Args:
            uow: 트랜잭션 관리를 위한 UnitOfWork 인스턴스

        Returns:
            UUID: 생성된 사용자의 ID

        Raises:
            ValueError: 사용자명이 이미 존재하는 경우
        """
        with uow:
            try:
                username = Username(self.username)
                password = Password(self.password)
            except Exception as e:
                return ValueError(e)

            user_repository: UserRepository = uow.get_repository(UserRepository)

            if user_repository.exists_by_username(username.value):
                raise ValueError("이미 존재하는 사용자명입니다")

            new_user = User(
                id=self._id_generator.generate(),
                username=username,
                hashed_password=HashedPassword(
                    self._password_hasher.hash(password.value)
                ),
            )

            user_repository.add(new_user)
            return new_user.id
