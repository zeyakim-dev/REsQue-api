import pytest
from dependency_injector import providers

from src.infrastructure.container import Container


class TestContainerConfiguration:
    @pytest.fixture
    def test_config(self):
        return {
            "persistence": {
                "type": "sqlite",
                "config": {
                    "url": "sqlite:///:memory:",
                    "connect_args": {"check_same_thread": False},
                },
            },
            "security": {
                "jwt_generator": {
                    "type": "jwt",
                    "config": {"jwt_secret": "test-secret", "jwt_expiry_minutes": 30},
                },
                "password_hasher": {
                    "type": "bcrypt",
                    "config": {"password_work_factor": 4},
                },
            },
            "message_bus": {
                "type": "rabbitmq",
                "config": {
                    "host": "localhost",
                    "port": 5672,
                    "username": "guest",
                    "password": "guest",
                    "exchange_name": "test_events",
                    "queue_name": None,
                },
            },
        }

    def test_container_has_required_providers(self):
        """컨테이너가 필요한 모든 프로바이더를 가지고 있는지 검증"""
        container = Container()

        # 필수 프로바이더 존재 확인
        essential_providers = [
            "config",
            "db_engine",
            "session_factory",
            "password_hasher",
            "token_generator",
            "id_generator",
            "uow",
            "message_bus",
        ]

        for provider in essential_providers:
            assert hasattr(
                container, provider
            ), f"Container should have {provider} provider"
            assert isinstance(getattr(container, provider), providers.Provider)

    def test_config_loading(self, test_config):
        """설정이 올바르게 로드되는지 검증"""
        container = Container()
        container.config.from_dict(test_config)

        # persistence 설정 검증
        assert container.config.persistence.type() == "sqlite"
        assert container.config.persistence.config.url() == "sqlite:///:memory:"
        assert (
            container.config.persistence.config.connect_args.check_same_thread()
            is False
        )

        # security 설정 검증
        assert container.config.security.jwt_generator.type() == "jwt"
        assert (
            container.config.security.jwt_generator.config.jwt_secret() == "test-secret"
        )
        assert container.config.security.jwt_generator.config.jwt_expiry_minutes() == 30

        assert container.config.security.password_hasher.type() == "bcrypt"
        assert (
            container.config.security.password_hasher.config.password_work_factor() == 4
        )

        # message_bus 설정 검증
        assert container.config.message_bus.type() == "rabbitmq"
        assert container.config.message_bus.config.host() == "localhost"
        assert container.config.message_bus.config.port() == 5672
        assert container.config.message_bus.config.username() == "guest"
        assert container.config.message_bus.config.password() == "guest"
        assert container.config.message_bus.config.exchange_name() == "test_events"
        assert container.config.message_bus.config.queue_name() is None

    def test_provider_dependencies(self):
        """프로바이더 간의 의존성이 올바르게 설정되었는지 검증"""
        container = Container()

        # providers.Singleton의 내부 구조 확인
        session_factory_provider = container.session_factory
        assert "db_engine" in session_factory_provider.kwargs
        assert session_factory_provider.kwargs["db_engine"] == container.db_engine

        # UoW의 의존성 확인
        uow_provider = container.uow
        assert "session_factory" in uow_provider.kwargs
        assert uow_provider.kwargs["session_factory"] == container.session_factory

        # message_bus의 의존성 확인
        message_bus_provider = container.message_bus
        assert "configuration" in message_bus_provider.kwargs
        assert message_bus_provider.kwargs["configuration"] == container.config

    def test_invalid_config_handling(self):
        """잘못된 설정 처리를 검증"""
        container = Container()

        with pytest.raises(Exception):  # 구체적인 예외 타입으로 변경 가능
            container.config.from_dict(
                {"invalid_section": {"invalid_key": "invalid_value"}}
            )
            # 필수 설정이 없는 상태에서 프로바이더 접근
            container.password_hasher()
