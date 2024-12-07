from dependency_injector import containers, providers

from src.infrastructure.message_bus.config import MessageBusFactory
from src.infrastructure.persistence import database_factory_factory
from src.infrastructure.persistence.database_factory_factory import (
    DatabaseFactoryFactory,
)
from src.infrastructure.security.security_factory import SecurityFactory
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator


class Container(containers.DeclarativeContainer):
    """의존성 주입을 위한 컨테이너 클래스입니다."""

    config = providers.Configuration()

    database_factory_factory = providers.Singleton(
        DatabaseFactoryFactory, configuration=config.persistence
    )

    database_factory = providers.Singleton(
        lambda f: f.create_database_factory(), f=database_factory_factory
    )

    db_engine = providers.Singleton(lambda f: f.create_engine(), f=database_factory)

    session_factory = providers.Singleton(
        lambda f, db_engine: f.create_session_factory(db_engine),
        f=database_factory,
        db_engine=db_engine,
    )

    uow = providers.Singleton(
        lambda f, session_factory: f.create_uow(session_factory),
        f=database_factory,
        session_factory=session_factory,
    )

    # 보안 컴포넌트
    password_hasher = providers.Singleton(
        SecurityFactory.create_password_hashser,
        configuration=config.security.password_hasher,
    )

    token_generator = providers.Singleton(
        SecurityFactory.create_jwt_token_generator,
        configuration=config.security.jwt_generator,
    )

    id_generator = providers.Singleton(UUIDv7Generator)

    # 메시지 버스 설정
    message_bus = providers.Singleton(
        MessageBusFactory.create_message_bus,
        configuration=config,
        command_handlers=providers.Dict(
            {
                "RegisterCommand": lambda cmd, uow: cmd.execute(uow),
                "LoginCommand": lambda cmd, uow: cmd.execute(uow),
            }
        ),
        event_handlers=providers.Dict({}),
    )
