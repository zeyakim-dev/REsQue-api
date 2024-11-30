from typing import Protocol
from dataclasses import dataclass

from src.application.commands.auth.register_command import RegisterCommand
from src.domain.user.user import User
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator


class UserRepository(Protocol):
    def save(self, user: User) -> None: ...


class LoginCommand(Protocol):
    def execute(self, user_repository, password_hasher):
        pass


class AuthService:
    def __init__(
        self,
        user_repository: UserRepository,
        password_hasher: PasswordHasher,
        id_generator: UUIDv7Generator,
    ):
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._id_generator = id_generator

    def register(self, command: RegisterCommand) -> None:
        command.execute(
            user_repository=self._user_repository,
            password_hasher=self._password_hasher,
            id_generator=self._id_generator,
        )

    def login(self, command: LoginCommand) -> None:
        command.execute(
            user_repository=self._user_repository,
            password_hasher=self._password_hasher,
        )
