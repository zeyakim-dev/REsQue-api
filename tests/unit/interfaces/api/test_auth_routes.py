from uuid import UUID

import pytest
from flask import Flask

from src.application.commands.auth.login_command import LoginResponse
from src.application.ports.message_bus import AbstractMessageBus
from src.application.ports.uow import UnitOfWork
from src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus import (
    RabbitMQMessageBus,
)
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.id.uuid_generator import UUIDv7Generator
from src.interfaces.api.auth_routes import authenticate, register


@pytest.fixture
def app():
    app = Flask(__name__)
    return app


@pytest.fixture
def message_bus(mocker):
    # 필요한 의존성들을 Mock으로 생성
    config = mocker.Mock()
    command_handlers = {}
    event_handlers = {}

    # RabbitMQMessageBus 자체를 Mock으로 대체
    mock_message_bus = mocker.Mock(spec=AbstractMessageBus)

    return mock_message_bus


@pytest.fixture
def uow(mocker):
    return mocker.create_autospec(UnitOfWork)


@pytest.fixture
def password_hasher(mocker):
    return mocker.create_autospec(PasswordHasher)


@pytest.fixture
def id_generator(mocker):
    return mocker.create_autospec(UUIDv7Generator)


@pytest.fixture
def token_generator(mocker):
    return mocker.create_autospec(JWTTokenGenerator)


class TestAuthRoutes:
    def test_register_success(
        self, app, message_bus, uow, password_hasher, id_generator
    ):
        # Given
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        message_bus.handle.return_value = user_id

        with app.test_request_context(
            "/auth/register",
            method="POST",
            json={"username": "testuser", "password": "password123"},
        ):
            # When
            response, status_code = register(
                message_bus=message_bus,
                uow=uow,
                password_hasher=password_hasher,
                id_generator=id_generator,
            )
            response_data = response.get_json()

            # Then
            assert status_code == 201
            assert response_data["id"] == str(user_id)
            message_bus.handle.assert_called_once()

    def test_register_handles_value_error(
        self, app, message_bus, uow, password_hasher, id_generator
    ):
        # Given
        message_bus.handle.side_effect = ValueError("이미 존재하는 사용자명입니다")

        with app.test_request_context(
            "/auth/register",
            method="POST",
            json={"username": "testuser", "password": "password123"},
        ):
            # When
            response, status_code = register(
                message_bus=message_bus,
                uow=uow,
                password_hasher=password_hasher,
                id_generator=id_generator,
            )
            response_data = response.get_json()

            # Then
            assert status_code == 400
            assert response_data["error"] == "이미 존재하는 사용자명입니다"

    def test_sign_in_success(
        self, app, message_bus, uow, password_hasher, token_generator
    ):
        # Given
        login_response = LoginResponse(
            access_token="test.jwt.token", token_type="Bearer"
        )
        message_bus.handle.return_value = login_response

        with app.test_request_context(
            "/auth/sign-in",
            method="POST",
            json={"username": "testuser", "password": "password123"},
        ):
            # When
            response, status_code = authenticate(
                message_bus=message_bus,
                uow=uow,
                password_hasher=password_hasher,
                token_generator=token_generator,
            )
            response_data = response.get_json()

            # Then
            assert status_code == 200
            assert response_data["access_token"] == "test.jwt.token"
            assert response_data["token_type"] == "Bearer"
            message_bus.handle.assert_called_once()

    def test_sign_in_handles_invalid_credentials(
        self, app, message_bus, uow, password_hasher, token_generator
    ):
        # Given
        message_bus.handle.side_effect = ValueError(
            "사용자명 또는 비밀번호가 올바르지 않습니다"
        )

        with app.test_request_context(
            "/auth/sign-in",
            method="POST",
            json={"username": "testuser", "password": "wrong_password"},
        ):
            # When
            response, status_code = authenticate(
                message_bus=message_bus,
                uow=uow,
                password_hasher=password_hasher,
                token_generator=token_generator,
            )
            response_data = response.get_json()

            # Then
            assert status_code == 401
            assert (
                response_data["error"] == "사용자명 또는 비밀번호가 올바르지 않습니다"
            )
