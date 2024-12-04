from datetime import timedelta
import time
from typing import Callable, Dict, Type
import docker
import pytest
import pika
from sqlalchemy import create_engine
from src.application.ports.repositories.user.user_repository import UserRepository
from src.infrastructure.message_bus.rabbit_mq.config import RabbitMQConfig
from sqlalchemy.orm import Session, sessionmaker

import logging

from src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus import RabbitMQMessageBus
from src.infrastructure.persistence.sqlalchemy.models.base import Base
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import SQLAlchemyRepository
from src.infrastructure.persistence.sqlalchemy.repositories.user_repository import SQLAlchemyUserRepository
from src.infrastructure.persistence.sqlalchemy.uow import SQLAlchemyUnitOfWork
from src.infrastructure.security.jwt_token_generator import JWTTokenGenerator
from src.infrastructure.security.password_hasher import PasswordHasher
from src.infrastructure.uuid.uuid_generator import UUIDv7Generator

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

@pytest.fixture(scope="session")
def rabbitmq_connection():
    """테스트에서 사용할 RabbitMQ 연결을 설정합니다."""
    config = RabbitMQConfig(
        host='localhost',
        port=5672,
        username='guest',
        password='guest',
        exchange_name='test_exchange',
        queue_name='test_queue'
    )
    
    # RabbitMQ 연결 설정
    credentials = pika.PlainCredentials(config.username, config.password)
    parameters = pika.ConnectionParameters(
        host=config.host,
        port=config.port,
        credentials=credentials,
        heartbeat=600,
        connection_attempts=3
    )
    
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    
    # 테스트용 exchange 및 queue 설정
    channel.exchange_declare(
        exchange=config.exchange_name,
        exchange_type='topic',
        durable=True
    )
    
    channel.queue_declare(
        queue=config.queue_name,
        durable=True
    )
    
    yield connection
    
    # 테스트 종료 후 정리
    try:
        channel.exchange_delete(config.exchange_name)
        channel.queue_delete(config.queue_name)
        connection.close()
    except:
        pass