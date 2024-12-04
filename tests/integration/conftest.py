import pytest
import pika
from src.infrastructure.message_bus.rabbit_mq.config import RabbitMQConfig

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