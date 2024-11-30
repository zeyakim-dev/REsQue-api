from typing import Any
from uuid import UUID
import pytest
from pytest_mock import MockerFixture

from src.domain.user.user import User
from src.application.service.auth.auth_service import AuthService
from src.application.commands.auth.register_command import RegisterCommand
from src.application.commands.auth.login_command import LoginCommand


class TestAuthService:
    @pytest.fixture(scope="class")
    def test_data(self) -> dict:
        return {
            "test_uuid": UUID("12345678-1234-5678-1234-567812345678"),
            "username": "testuser",
            "password": "password123",
            "hashed_password": "hashed_password_123",
        }

    @pytest.fixture
    def mock_user_repository(self, mocker: MockerFixture) -> Any:
        return mocker.Mock(spec=["save"])

    @pytest.fixture
    def mock_password_hasher(self, mocker: MockerFixture, test_data: dict) -> Any:
        hasher = mocker.Mock()
        hasher.hash.return_value = test_data["hashed_password"]
        return hasher

    @pytest.fixture
    def mock_id_generator(self, mocker: MockerFixture, test_data: dict) -> Any:
        generator = mocker.Mock()
        generator.generate.return_value = test_data["test_uuid"]
        return generator

    @pytest.fixture
    def auth_service(
        self,
        mock_user_repository: Any,
        mock_password_hasher: Any,
        mock_id_generator: Any,
    ) -> AuthService:
        return AuthService(
            user_repository=mock_user_repository,
            password_hasher=mock_password_hasher,
            id_generator=mock_id_generator,
        )

    @pytest.fixture
    def mock_register_command(self, mocker: MockerFixture) -> Any:
        return mocker.Mock(spec=RegisterCommand)

    @pytest.fixture
    def mock_login_command(self, mocker: MockerFixture) -> Any:
        return mocker.Mock(spec=LoginCommand)

    def test_register_executes_command_with_correct_dependencies(
        self,
        auth_service: AuthService,
        mock_register_command: Any,
        mock_user_repository: Any,
        mock_password_hasher: Any,
        mock_id_generator: Any,
    ) -> None:
        """
        register 메서드 테스트
        1. command.execute가 올바른 의존성과 함께 호출되는지 검증
        """
        # When
        auth_service.register(mock_register_command)

        # Then
        mock_register_command.execute.assert_called_once_with(
            user_repository=mock_user_repository,
            password_hasher=mock_password_hasher,
            id_generator=mock_id_generator,
        )

    def test_register_propagates_command_execution_error(
        self, auth_service: AuthService, mock_register_command: Any
    ) -> None:
        """
        register 메서드가 command 실행 중 발생한 예외를 전파하는지 검증
        """
        # Given
        mock_register_command.execute.side_effect = ValueError("회원가입 실패")

        # When/Then
        with pytest.raises(ValueError, match="회원가입 실패"):
            auth_service.register(mock_register_command)

    def test_login_executes_command_with_correct_dependencies(
        self,
        auth_service: AuthService,
        mock_login_command: Any,
        mock_user_repository: Any,
        mock_password_hasher: Any,
    ) -> None:
        """
        login 메서드 테스트
        1. command.execute가 올바른 의존성과 함께 호출되는지 검증
        """
        # When
        auth_service.login(mock_login_command)

        # Then
        mock_login_command.execute.assert_called_once_with(
            user_repository=mock_user_repository, password_hasher=mock_password_hasher
        )

    def test_login_propagates_command_execution_error(
        self, auth_service: AuthService, mock_login_command: Any
    ) -> None:
        """
        login 메서드가 command 실행 중 발생한 예외를 전파하는지 검증
        """
        # Given
        mock_login_command.execute.side_effect = ValueError("로그인 실패")

        # When/Then
        with pytest.raises(ValueError, match="로그인 실패"):
            auth_service.login(mock_login_command)
