from uuid import UUID

import pytest

from src.application.commands.auth.login_command import LoginCommand, LoginResponse
from src.application.commands.auth.register_command import RegisterCommand
from src.application.ports.repositories.user.user_repository import UserRepository
from src.domain.user.user import User
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import (
    SQLAlchemyUserRepository,
)


class TestAuthIntegration:
    def test_user_registration_and_login_flow(
        self, message_bus, uow, password_hasher, token_generator, id_generator
    ):
        """사용자 등록부터 로그인까지의 전체 흐름을 테스트합니다."""
        # Given
        username = "testuser"
        password = "Password123!"

        # When - 사용자 등록
        register_command = RegisterCommand(
            username=username,
            password=password,
            _password_hasher=password_hasher,
            _id_generator=id_generator,
        )

        # MessageBus를 통한 명령 실행
        user_id = message_bus.handle(register_command, uow)[0]

        # Then - 등록 결과 확인
        assert isinstance(user_id, UUID)

        with uow:
            user_repo = uow.get_repository(UserRepository)
            saved_user = user_repo.find_by_username(username)
            assert isinstance(saved_user, User)
            assert password_hasher.verify(password, saved_user.hashed_password)

        # When - 로그인
        login_command = LoginCommand(
            username=username,
            password=password,
            _password_hasher=password_hasher,
            _token_generator=token_generator,
        )
        login_response = message_bus.handle(login_command, uow)[0]

        # Then - 로그인 결과 확인
        assert isinstance(login_response, LoginResponse)
        assert login_response.access_token is not None
        assert login_response.token_type == "Bearer"

    def test_login_with_wrong_password(
        self, message_bus, uow, password_hasher, token_generator, id_generator
    ):
        """잘못된 비밀번호로 로그인 시도 시 실패하는지 테스트합니다."""
        # Given
        username = "testuser2"
        password = "Password123!"
        wrong_password = "WrongPassword123!"

        # 사용자 등록
        register_command = RegisterCommand(
            username=username,
            password=password,
            _password_hasher=password_hasher,
            _id_generator=id_generator,
        )
        message_bus.handle(register_command, uow)

        # When & Then - 잘못된 비밀번호로 로그인
        login_command = LoginCommand(
            username=username,
            password=wrong_password,
            _password_hasher=password_hasher,
            _token_generator=token_generator,
        )
        with pytest.raises(
            ValueError, match="사용자명 또는 비밀번호가 올바르지 않습니다"
        ):
            message_bus.handle(login_command, uow)

    def test_duplicate_username_registration(
        self, message_bus, uow, password_hasher, id_generator
    ):
        """중복된 사용자명으로 등록 시 실패하는지 테스트합니다."""
        # Given
        username = "testuser3"
        password = "Password123!"

        # 첫 번째 사용자 등록
        register_command = RegisterCommand(
            username=username,
            password=password,
            _password_hasher=password_hasher,
            _id_generator=id_generator,
        )
        message_bus.handle(register_command, uow)

        # When & Then - 동일한 사용자명으로 다시 등록
        duplicate_command = RegisterCommand(
            username=username,
            password="DifferentPass123!",
            _password_hasher=password_hasher,
            _id_generator=id_generator,
        )
        with pytest.raises(ValueError, match="이미 존재하는 사용자명입니다"):
            message_bus.handle(duplicate_command, uow)
