import pytest
from unittest.mock import MagicMock, patch, call
from datetime import datetime
import json
from dataclasses import dataclass
from uuid import UUID

from src.application.commands.command import Command
from src.application.events.event import Event
from src.application.ports.uow import UnitOfWork
from src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus import RabbitMQMessageBus

# 테스트용 더미 클래스들
@dataclass
class TestCommand(Command):
    id: UUID
    data: str
    
    def execute(self, uow: UnitOfWork):
        return f"Executed {self.data}"

@dataclass
class TestEvent(Event):
    id: UUID
    message: str

class TestUnitOfWork:
    def __init__(self):
        self.committed = False
        self.events = []
    
    def collect_new_events(self):
        return self.events

    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        pass

@pytest.fixture
def config():
    return {
        'host': 'localhost',
        'port': 5672,
        'username': 'guest',
        'password': 'guest',
        'exchange_name': 'test_exchange',
        'queue_name': 'test_queue'
    }

@pytest.fixture
def mock_pika():
    with patch('src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus.pika') as mock:
        # BlockingConnection 설정
        mock_connection = MagicMock()
        mock_channel = MagicMock()
        mock_connection.channel.return_value = mock_channel
        mock.BlockingConnection.return_value = mock_connection
        
        yield mock

@pytest.fixture
def command_handlers():
    def handle_test_command(command: TestCommand, uow: UnitOfWork):
        return command.execute(uow)
    
    return {
        'TestCommand': handle_test_command
    }

@pytest.fixture
def event_handlers():
    def handle_test_event(event: TestEvent, uow: UnitOfWork):
        pass
    
    return {
        'TestEvent': [handle_test_event]
    }

@pytest.fixture
def message_bus(config, mock_pika, command_handlers, event_handlers):
    return RabbitMQMessageBus(config, command_handlers, event_handlers)

class TestRabbitMQMessageBus:
    def test_initialization(self, message_bus, mock_pika, config):
        """메시지 버스 초기화 테스트"""
        # connection 설정 검증
        mock_pika.PlainCredentials.assert_called_once_with(
            config['username'], 
            config['password']
        )
        
        mock_pika.ConnectionParameters.assert_called_once()
        args = mock_pika.ConnectionParameters.call_args
        assert args.kwargs['host'] == config['host']
        assert args.kwargs['port'] == config['port']
        
        # exchange 선언 검증
        channel = message_bus.channel
        channel.exchange_declare.assert_called_once_with(
            exchange=config['exchange_name'],
            exchange_type='topic',
            durable=True
        )
        
        # queue 선언 검증
        channel.queue_declare.assert_called_once_with(
            queue=config['queue_name'],
            durable=True
        )

    def test_handle_command(self, message_bus):
        """커맨드 처리 테스트"""
        command = TestCommand(id=UUID('12345678-1234-5678-1234-567812345678'), data="test")
        uow = TestUnitOfWork()
        
        result = message_bus._handle_command(command, uow)
        
        assert result == "Executed test"

    def test_handle_command_with_invalid_type(self, message_bus):
        """등록되지 않은 커맨드 타입 처리 테스트"""
        @dataclass
        class UnknownCommand(Command):
            data: str
            
            def execute(self, uow: UnitOfWork):
                pass
        
        command = UnknownCommand(data="test")
        uow = TestUnitOfWork()
        
        with pytest.raises(ValueError, match="No handler registered for command UnknownCommand"):
            message_bus._handle_command(command, uow)

    def test_handle_event(self, message_bus):
        """이벤트 처리 테스트"""
        event = TestEvent(id=UUID('12345678-1234-5678-1234-567812345678'), message="test")
        uow = TestUnitOfWork()
        
        # 예외가 발생하지 않아야 함
        message_bus._handle_event(event, uow)

    def test_publish_event(self, message_bus):
        """이벤트 발행 테스트"""
        event_id = UUID('12345678-1234-5678-1234-567812345678')
        event = TestEvent(id=event_id, message="test")
        
        message_bus._publish_event(event)
        
        channel = message_bus.channel
        channel.basic_publish.assert_called_once()
        
        # 발행된 메시지 검증
        args = channel.basic_publish.call_args
        assert args.kwargs['exchange'] == 'test_exchange'
        assert args.kwargs['routing_key'] == 'TestEvent'
        
        published_message = json.loads(args.kwargs['body'])
        assert published_message['type'] == 'TestEvent'
        assert published_message['data']['id'] == str(event_id)  # UUID가 문자열로 변환되어 있는지 확인
        assert published_message['data']['message'] == 'test'
        assert 'timestamp' in published_message

    def test_publish_error(self, message_bus):
        """에러 발행 테스트"""
        command = TestCommand(id=UUID('12345678-1234-5678-1234-567812345678'), data="test")
        error = ValueError("테스트 에러")
        
        message_bus._publish_error(command, error)
        
        channel = message_bus.channel
        channel.basic_publish.assert_called_once()
        
        # 발행된 에러 메시지 검증
        args = channel.basic_publish.call_args
        assert args.kwargs['exchange'] == 'test_exchange'
        assert args.kwargs['routing_key'] == 'error'
        
        error_message = json.loads(args.kwargs['body'])