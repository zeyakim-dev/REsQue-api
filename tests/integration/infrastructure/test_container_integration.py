from datetime import datetime, timedelta
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.application.ports.repositories.user.user_repository import UserRepository
from src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus import (
    RabbitMQMessageBus,
)
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import (
    SQLAlchemyUserRepository,
)
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator


class TestContainerIntegration:
    @pytest.fixture(scope="class")
    def configured_container(self, app):
        """실제 설정이 로드된 컨테이너"""
        return app.extensions["di_container"]

    def test_database_components_integration(self, configured_container):
        """데이터베이스 관련 컴포넌트들이 실제로 작동하는지 검증"""
        # 엔진, 세션팩토리 및 세션 생성
        engine = configured_container.db_engine()
        assert engine is not None

        session_factory = configured_container.session_factory()
        session = session_factory()

        try:
            # 실제 쿼리 실행 검증
            result = session.execute(text("SELECT 1")).scalar()
            assert result == 1
        finally:
            session.close()

    def test_security_components_integration(self, configured_container):
        """보안 관련 컴포넌트들이 실제로 작동하는지 검증"""
        # 비밀번호 해셔 검증
        hasher = configured_container.password_hasher()
        assert isinstance(hasher, PasswordHasher)

        test_password = "test123!"
        hashed = hasher.hash(test_password)
        assert hasher.verify(test_password, hashed)

        # 토큰 생성기 검증
        token_generator = configured_container.token_generator()
        assert isinstance(token_generator, JWTTokenGenerator)

        test_payload = {"sub": "test", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = token_generator.generate_token(test_payload)
        assert isinstance(token, str)

    def test_id_generator_integration(self, configured_container):
        """ID 생성기가 실제로 작동하는지 검증"""
        generator = configured_container.id_generator()
        assert isinstance(generator, UUIDv7Generator)

        generated_id = generator.generate()
        assert isinstance(generated_id, UUID)
        # UUIDv7 형식 검증 (시간 기반)
        assert generated_id.version == 7

    def test_repository_integration(self, configured_container):
        """레포지토리가 UoW를 통해 실제로 작동하는지 검증"""
        uow = configured_container.uow()

        # UoW 컨텍스트 외부에서는 세션이 없어야 함
        with pytest.raises(RuntimeError):
            uow.get_repository(SQLAlchemyUserRepository)

        with uow:
            # 레포지토리 가져오기
            user_repo = uow.get_repository(UserRepository)
            assert user_repo is not None

            # 실제 데이터베이스 연결 확인
            current_session = getattr(user_repo, "_session", None)
            assert isinstance(current_session, Session)
            assert current_session.is_active  # 세션이 활성 상태여야 함

    def test_message_bus_integration(self, configured_container, rabbitmq_container):
        """메시지 버스가 RabbitMQ와 실제로 연동되는지 검증"""
        message_bus = configured_container.message_bus()
        assert isinstance(message_bus, RabbitMQMessageBus)

        # RabbitMQ 연결 상태 확인
        assert message_bus.connection.is_open
        assert message_bus.channel.is_open

        # Exchange 존재 확인
        message_bus.channel.exchange_declare(
            exchange=message_bus.config["exchange_name"],
            exchange_type="topic",
            passive=True,  # 존재하는지만 확인
        )

    def test_complete_container_lifecycle(
        self, configured_container, rabbitmq_container
    ):
        """전체 컴포넌트들이 함께 잘 작동하는지 검증"""
        # 1. 필요한 컴포넌트들 생성
        uow = configured_container.uow()
        message_bus = configured_container.message_bus()
        hasher = configured_container.password_hasher()
        id_gen = configured_container.id_generator()

        # 2. 컴포넌트들이 모두 생성되었는지 확인
        assert uow is not None
        assert message_bus is not None
        assert hasher is not None
        assert id_gen is not None

        # 3. 기본적인 작동 확인
        try:
            with uow:
                user_repo = uow.get_repository(UserRepository)
                assert user_repo is not None
        except Exception as e:
            pytest.fail(f"UoW transaction failed: {str(e)}")

        # 4. 메시지 버스 연결 상태
        assert message_bus.connection.is_open

        # 5. 컴포넌트 정리
        message_bus.close()
