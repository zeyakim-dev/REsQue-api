from dataclasses import dataclass
from typing import Optional

from src.application.commands.command import Command
from src.application.ports.repositories.user.user_repository import UserRepository
from src.application.ports.uow import UnitOfWork
from src.domain.user.user import User
from src.domain.user.values import Password, Username
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher


@dataclass(frozen=True)
class LoginResponse:
    """로그인 응답 데이터입니다."""

    access_token: str
    token_type: str = "Bearer"


@dataclass(frozen=True)
class LoginCommand(Command[LoginResponse]):
    """JWT 토큰을 발급하는 로그인 커맨드입니다."""

    username: str
    password: str
    _password_hasher: PasswordHasher
    _token_generator: JWTTokenGenerator

    def execute(self, uow: UnitOfWork) -> LoginResponse:
        with uow:
            try:
                username = Username(self.username)
                password = Password(self.password)
            except Exception as e:
                raise ValueError(str(e))

            user_repository: UserRepository = uow.get_repository(UserRepository)

            user = user_repository.find_by_username(username.value)
            if not user:
                raise ValueError("사용자명 또는 비밀번호가 올바르지 않습니다")

            if not self._password_hasher.verify(
                password=password.value, hashed_password=user.hashed_password.value
            ):
                raise ValueError("사용자명 또는 비밀번호가 올바르지 않습니다")

            token_payload = {"sub": str(user.id), "username": str(user.username)}

            return LoginResponse(
                access_token=self._token_generator.generate_token(token_payload)
            )
