from dependency_injector import containers, providers
from sqlalchemy.orm import sessionmaker
from src.application.ports.repositories.user.user_repository import UserRepository
from src.infrastructure.message_bus.config import MessageBusFactory
from src.infrastructure.persistence.database_factory import DatabaseFactory
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.persistence.sqlalchemy.uow import SQLAlchemyUnitOfWork
from src.infrastructure.security.security_factory import SecurityFactory
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator


class Container(containers.DeclarativeContainer):
    """의존성 주입을 위한 컨테이너 클래스입니다."""
    
    config = providers.Configuration()


    # 데이터베이스 엔진을 생성할 때 설정을 동적으로 결정합니다
    db_engine = providers.Singleton(
        DatabaseFactory.create_engine,
        configuration=config
    )
    
    session_factory = providers.Singleton(
        sessionmaker,
        bind=db_engine
    )
    
    # 보안 관련 컴포넌트들
    # 단순하고 직접적인 설정값 전달
    password_hasher = providers.Singleton(
        SecurityFactory.create_password_hashser,
        configuration=config
    )
    
    token_generator = providers.Singleton(
        SecurityFactory.create_jwt_token_generator,
        configuration=config
    )
    
    id_generator = providers.Singleton(UUIDv7Generator)
    
    # 레포지토리 계층
    # 의존성 주입의 기본에 충실한 구성
    repository_factories = providers.Dict({
        UserRepository: lambda session: SQLAlchemyUserRepository(session=session)
    })
    
    uow = providers.Singleton(
        SQLAlchemyUnitOfWork,
        session_factory=session_factory,
        repositories=repository_factories
    )
    
    # 메시지 버스 설정
    message_bus = providers.Singleton(
        MessageBusFactory.create_message_bus,
        configuration=config,
        command_handlers=providers.Dict({
            'RegisterCommand': lambda cmd, uow: cmd.execute(uow),
            'LoginCommand': lambda cmd, uow: cmd.execute(uow)
        }),
        event_handlers=providers.Dict({})
    )