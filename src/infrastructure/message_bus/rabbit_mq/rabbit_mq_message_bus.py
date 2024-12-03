from datetime import datetime
import json
import logging
from typing import Any, Dict, List
import pika
from dataclasses import asdict

from src.application.commands.command import Command
from src.application.events.event import Event
from src.application.ports.uow import UnitOfWork
from src.application.ports.message_bus import AbstractMessageBus, Message
from .config import RabbitMQConfig

logger = logging.getLogger(__name__)

class RabbitMQMessageBus(AbstractMessageBus):
    def __init__(
        self,
        config: RabbitMQConfig,
        command_handlers: Dict[str, Any],
        event_handlers: Dict[str, List[Any]]
    ):
        self.config = config
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers
        
        # RabbitMQ 연결 설정
        credentials = pika.PlainCredentials(config.username, config.password)
        parameters = pika.ConnectionParameters(
            host=config.host,
            port=config.port,
            credentials=credentials,
            heartbeat=600,
            connection_attempts=3
        )
        
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        
        # Exchange 설정
        self.channel.exchange_declare(
            exchange=config.exchange_name,
            exchange_type='topic',
            durable=True
        )
        
        # 큐 설정 (지정된 경우)
        if config.queue_name:
            self.channel.queue_declare(
                queue=config.queue_name,
                durable=True
            )
    
    def _handle_command(self, command: Command, uow: UnitOfWork) -> Any:
        """커맨드를 처리하고 결과를 반환합니다."""
        command_type = command.__class__.__name__
        handler = self.command_handlers.get(command_type)
        
        if not handler:
            raise ValueError(f"No handler registered for command {command_type}")
            
        try:
            return handler(command, uow)
        except Exception as e:
            logger.error(f"Error handling command {command_type}: {str(e)}")
            raise

    def _handle_event(self, event: Event, uow: UnitOfWork) -> None:
        """이벤트를 처리합니다."""
        event_type = event.__class__.__name__
        handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                handler(event, uow)
            except Exception as e:
                logger.error(f"Error handling event {event_type}: {str(e)}")
                self._publish_error(event, e)

    def _collect_new_events(self, uow: UnitOfWork) -> List[Event]:
        """UoW에서 새로운 이벤트를 수집합니다."""
        return uow.collect_new_events()

    def _publish_event(self, event: Event) -> None:
        """이벤트를 RabbitMQ에 발행합니다."""
        event_type = event.__class__.__name__
        
        try:
            message = {
                "type": event_type,
                "data": asdict(event) if hasattr(event, '__dataclass_fields__') else vars(event),
                "timestamp": datetime.now().isoformat()
            }
            
            self.channel.basic_publish(
                exchange=self.config.exchange_name,
                routing_key=event_type,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # persistent message
                    content_type='application/json'
                )
            )
            
            logger.info(f"Published event {event_type}")
            
        except Exception as e:
            logger.error(f"Error publishing event {event_type}: {str(e)}")
            raise

    def _publish_error(self, message: Message, error: Exception) -> None:
        """에러 정보를 RabbitMQ에 발행합니다."""
        try:
            error_message = {
                "message_type": message.__class__.__name__,
                "error": str(error),
                "timestamp": datetime.now().isoformat()
            }
            
            self.channel.basic_publish(
                exchange=self.config.exchange_name,
                routing_key="error",
                body=json.dumps(error_message),
                properties=pika.BasicProperties(
                    delivery_mode=2,
                    content_type='application/json'
                )
            )
            
        except Exception as e:
            logger.error(f"Error publishing error message: {str(e)}")

    def start_consuming(self) -> None:
        """메시지 소비를 시작합니다."""
        if not self.config.queue_name:
            raise ValueError("Queue name must be configured to start consuming")

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                # 메시지 처리 로직 구현
                logger.info(f"Received message: {message}")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}")
                
        self.channel.basic_consume(
            queue=self.config.queue_name,
            on_message_callback=callback,
            auto_ack=True
        )
        
        logger.info(f"Start consuming from queue: {self.config.queue_name}")
        self.channel.start_consuming()

    def close(self) -> None:
        """연결을 종료합니다."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("RabbitMQ connection closed")