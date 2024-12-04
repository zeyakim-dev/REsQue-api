from uuid import UUID
import pika
import pytest
import docker
import time
from datetime import timedelta
from typing import Dict, Type, Callable
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.application.commands.auth.login_command import LoginCommand, LoginResponse
from src.application.commands.auth.register_command import RegisterCommand
from src.application.ports.repositories.user.user_repository import UserRepository
from src.infrastructure.message_bus.rabbit_mq.config import RabbitMQConfig
from src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus import RabbitMQMessageBus
from src.infrastructure.persistence.sqlalchemy.models.base import Base
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.persistence.sqlalchemy.uow import SQLAlchemyUnitOfWork
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator

import pytest
import docker
import time
import pika
from uuid import UUID
from datetime import timedelta
from typing import Dict, Type, Callable
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import logging

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def rabbitmq_container():
    """테스트용 RabbitMQ 컨테이너를 실행하고 관리합니다."""
    client = docker.from_env()
    
    # 기존 컨테이너 정리
    try:
        container = client.containers.get('test-rabbitmq')
        container.stop()
        container.remove()
    except:
        pass
        
    # 새 컨테이너 실행
    container = client.containers.run(
        "rabbitmq:3-management",
        name='test-rabbitmq',
        ports={'5672/tcp': 5672, '15672/tcp': 15672},
        environment={
            'RABBITMQ_DEFAULT_USER': 'guest',
            'RABBITMQ_DEFAULT_PASS': 'guest'
        },
        detach=True,
        remove=True
    )
    
    # 서비스 시작 대기
    logger.info("RabbitMQ 컨테이너 시작 중...")
    time.sleep(10)  # RabbitMQ 서비스가 완전히 시작될 때까지 대기
    
    yield container
    
    # 컨테이너 정리
    try:
        container.stop()
    except:
        pass

@pytest.fixture(scope="session")
def rabbitmq_config():
    return RabbitMQConfig(
        host='localhost',
        port=5672,
        username='guest',
        password='guest',
        exchange_name='test_exchange',
        queue_name='test_queue'
    )

@pytest.fixture
def message_bus(rabbitmq_container, rabbitmq_config, command_handlers, event_handlers):
    """RabbitMQ 메시지 버스를 설정하고 연결을 관리합니다."""
    max_retries = 5
    retry_count = 0
    last_error = None
    
    while retry_count < max_retries:
        try:
            logger.info(f"RabbitMQ 연결 시도 중... (시도 {retry_count + 1}/{max_retries})")
            message_bus = RabbitMQMessageBus(
                config=rabbitmq_config,
                command_handlers=command_handlers,
                event_handlers=event_handlers
            )
            logger.info("RabbitMQ 연결 성공")
            break
        except pika.exceptions.AMQPConnectionError as e:
            last_error = e
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"RabbitMQ 연결 실패, 재시도 중... ({retry_count}/{max_retries})")
                time.sleep(5)  # 재시도 전 대기 시간 증가
            else:
                logger.error("RabbitMQ 연결 최종 실패")
                pytest.fail(f"RabbitMQ 연결 실패: {last_error}")
    
    yield message_bus
    
    try:
        message_bus.close()
    except Exception as e:
        logger.warning(f"메시지 버스 종료 중 오류 발생: {e}")

@pytest.fixture(autouse=True)
def cleanup_rabbitmq(rabbitmq_container, rabbitmq_config):
    """각 테스트 후 RabbitMQ 큐와 교환기를 정리합니다."""
    yield
    
    try:
        credentials = pika.PlainCredentials(
            rabbitmq_config.username,
            rabbitmq_config.password
        )
        parameters = pika.ConnectionParameters(
            host=rabbitmq_config.host,
            port=rabbitmq_config.port,
            credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        
        # 큐와 교환기 제거
        channel.queue_delete(queue=rabbitmq_config.queue_name)
        channel.exchange_delete(exchange=rabbitmq_config.exchange_name)
        
        connection.close()
    except Exception as e:
        logger.warning(f"RabbitMQ 정리 중 오류 발생: {e}")

@pytest.fixture
def command_handlers(password_hasher, id_generator, token_generator):
    """명령 핸들러를 등록합니다."""
    def register_handler(command, uow):
        return command.execute(uow)
        
    def login_handler(command, uow):
        return command.execute(uow)
        
    return {
        'RegisterCommand': register_handler,
        'LoginCommand': login_handler
    }

@pytest.fixture
def event_handlers():
    """이벤트 핸들러를 등록합니다."""
    return {}

@pytest.fixture(scope="session")
def engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)

@pytest.fixture
def repository_factories() -> Dict[Type[SQLAlchemyRepository], Callable[[Session], SQLAlchemyRepository]]:
    return {
        UserRepository: lambda session: SQLAlchemyUserRepository(session)
    }

@pytest.fixture
def db_session(engine):
    Session = sessionmaker(bind=engine)
    session = Session()
    transaction = session.begin()
    
    yield session

    if transaction.is_active:
        transaction.rollback()
    session.close()

@pytest.fixture
def uow(db_session, repository_factories):
    def session_factory():
        return db_session
        
    return SQLAlchemyUnitOfWork(
        session_factory=session_factory,
        repositories=repository_factories
    )

@pytest.fixture(scope="class")
def password_hasher():
    return PasswordHasher()

@pytest.fixture(scope="class")
def token_generator():
    return JWTTokenGenerator(
        secret_key="test_secret",
        token_expiry=timedelta(hours=1)
    )

@pytest.fixture(scope="class")
def id_generator():
    return UUIDv7Generator()

@pytest.fixture
def message_bus(rabbitmq_config, command_handlers, event_handlers):
    message_bus = RabbitMQMessageBus(
        config=rabbitmq_config,
        command_handlers=command_handlers,
        event_handlers=event_handlers
    )
    yield message_bus
    message_bus.close()

class TestAuthIntegration:
    def test_user_registration_and_login_flow(
        self,
        message_bus,
        uow,
        password_hasher,
        token_generator,
        id_generator
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
            _id_generator=id_generator
        )
        
        # MessageBus를 통한 명령 실행
        user_id = message_bus.handle(register_command, uow)[0]
        
        # Then - 등록 결과 확인
        assert isinstance(user_id, UUID)

        with uow:
            user_repo = uow.get_repository(UserRepository)
            saved_user = user_repo.find_by_username(username)
            assert password_hasher.verify(password, saved_user.hashed_password)

        # When - 로그인
        login_command = LoginCommand(
            username=username,
            password=password,
            _password_hasher=password_hasher,
            _token_generator=token_generator
        )
        login_response = message_bus.handle(login_command, uow)[0]

        # Then - 로그인 결과 확인
        assert isinstance(login_response, LoginResponse)
        assert login_response.access_token is not None
        assert login_response.token_type == "Bearer"
    
    def test_login_with_wrong_password(
        self,
        message_bus,
        uow,
        password_hasher,
        token_generator,
        id_generator
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
            _id_generator=id_generator
        )
        message_bus.handle(register_command, uow)

        # When & Then - 잘못된 비밀번호로 로그인
        login_command = LoginCommand(
            username=username,
            password=wrong_password,
            _password_hasher=password_hasher,
            _token_generator=token_generator
        )
        with pytest.raises(ValueError, match="사용자명 또는 비밀번호가 올바르지 않습니다"):
            message_bus.handle(login_command, uow)

    def test_duplicate_username_registration(
        self,
        message_bus,
        uow,
        password_hasher,
        id_generator
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
            _id_generator=id_generator
        )
        message_bus.handle(register_command, uow)

        # When & Then - 동일한 사용자명으로 다시 등록
        duplicate_command = RegisterCommand(
            username=username,
            password="DifferentPass123!",
            _password_hasher=password_hasher,
            _id_generator=id_generator
        )
        with pytest.raises(ValueError, match="이미 존재하는 사용자명입니다"):
            message_bus.handle(duplicate_command, uow)