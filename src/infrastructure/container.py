from datetime import timedelta
from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.ports.repositories.user.user_repository import UserRepository
from src.infrastructure.message_bus.rabbit_mq.config import RabbitMQConfig
from src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus import RabbitMQMessageBus
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import SQLAlchemyUserRepository, UserRepository
from src.infrastructure.persistence.sqlalchemy.uow import SQLAlchemyUnitOfWork
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator

class Container(containers.DeclarativeContainer):
    """의존성 주입을 위한 컨테이너 클래스입니다."""
    
    # 설정
    config = providers.Configuration()
    
    # 데이터베이스
    db_engine = providers.Singleton(
        create_engine,
        config.db.url
    )
    
    session_factory = providers.Singleton(
        sessionmaker,
        bind=db_engine
    )
    
    # 인프라스트럭처 컴포넌트
    password_hasher = providers.Singleton(
        PasswordHasher,
        work_factor=config.security.password_work_factor
    )
    
    token_generator = providers.Singleton(
        JWTTokenGenerator,
        secret_key=config.security.jwt_secret,
        token_expiry=providers.Factory(
            timedelta,
            minutes=config.security.jwt_expiry_minutes
        )
    )
    
    id_generator = providers.Singleton(UUIDv7Generator)
    
    # 레포지토리
    user_repository = providers.Factory(
        SQLAlchemyUserRepository,
        session=session_factory
    )
    
    # Repository 팩토리 딕셔너리
    repository_factories = providers.Dict({
        UserRepository: user_repository
    })
    
    # UnitOfWork
    uow = providers.Singleton(
        SQLAlchemyUnitOfWork,
        session_factory=session_factory,
        repositories=repository_factories
    )
    
    # RabbitMQ 설정
    rabbitmq_config = providers.Factory(
        RabbitMQConfig,
        host=config.rabbitmq.host,
        port=config.rabbitmq.port,
        username=config.rabbitmq.username,
        password=config.rabbitmq.password,
        exchange_name=config.rabbitmq.exchange_name,
        queue_name=config.rabbitmq.queue_name
    )
    
    # 메시지 버스
    message_bus = providers.Singleton(
        RabbitMQMessageBus,
        config=rabbitmq_config,
        command_handlers=providers.Dict({
            'RegisterCommand': lambda cmd, uow: cmd.execute(uow),
            'LoginCommand': lambda cmd, uow: cmd.execute(uow)
        }),
        event_handlers=providers.Dict({})
    )