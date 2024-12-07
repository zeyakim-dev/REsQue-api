import json
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

import pika

from src.application.commands.command import Command
from src.application.events.event import Event
from src.application.ports.message_bus import AbstractMessageBus, Message
from src.application.ports.uow import UnitOfWork


class RabbitMQMessageBus(AbstractMessageBus):
    def __init__(
        self,
        config: Dict[str, Any],
        command_handlers: Dict[str, Any],
        event_handlers: Dict[str, List[Any]],
    ):
        self.config = config
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers

        # RabbitMQ 연결 설정
        credentials = pika.PlainCredentials(
            config.get("username", "guest"), config.get("password", "guest")
        )
        parameters = pika.ConnectionParameters(
            host=config.get("host", "localhost"),
            port=config.get("port", 5672),
            credentials=credentials,
            heartbeat=600,
            connection_attempts=3,
        )

        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()

        # Exchange 설정
        self.channel.exchange_declare(
            exchange=config.get("exchange_name", "domain_events"),
            exchange_type="topic",
            durable=True,
        )

        # 큐 설정 (지정된 경우)
        queue_name = config.get("queue_name")
        if queue_name:
            self.channel.queue_declare(queue=queue_name, durable=True)

    def _handle_command(self, command: Command, uow: UnitOfWork) -> Any:
        """커맨드를 처리하고 결과를 반환합니다."""
        command_type = command.__class__.__name__
        handler = self.command_handlers.get(command_type)

        if not handler:
            raise ValueError(f"No handler registered for command {command_type}")

        try:
            return handler(command, uow)
        except Exception as e:
            raise

    def _handle_event(self, event: Event, uow: UnitOfWork) -> None:
        """이벤트를 처리합니다."""
        event_type = event.__class__.__name__
        handlers = self.event_handlers.get(event_type, [])

        for handler in handlers:
            try:
                handler(event, uow)
            except Exception as e:
                self._publish_error(event, e)

    def _collect_new_events(self, uow: UnitOfWork) -> List[Event]:
        """UoW에서 새로운 이벤트를 수집합니다."""
        return uow.collect_new_events()

    def _publish_event(self, event: Event) -> None:
        """이벤트를 RabbitMQ에 발행합니다."""
        event_type = event.__class__.__name__

        try:

            class UUIDEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, UUID):
                        return str(obj)
                    return super().default(obj)

            message = {
                "type": event_type,
                "data": (
                    asdict(event)
                    if hasattr(event, "__dataclass_fields__")
                    else vars(event)
                ),
                "timestamp": datetime.now().isoformat(),
            }

            self.channel.basic_publish(
                exchange=self.config.get("exchange_name", "domain_events"),
                routing_key=event_type,
                body=json.dumps(message, cls=UUIDEncoder),
                properties=pika.BasicProperties(
                    delivery_mode=2, content_type="application/json"
                ),
            )

        except Exception as e:
            raise

    def _publish_error(self, message: Message, error: Exception) -> None:
        """에러 정보를 RabbitMQ에 발행합니다."""
        try:
            error_message = {
                "message_type": message.__class__.__name__,
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
            }

            self.channel.basic_publish(
                exchange=self.config.get("exchange_name", "domain_events"),
                routing_key="error",
                body=json.dumps(error_message),
                properties=pika.BasicProperties(
                    delivery_mode=2, content_type="application/json"
                ),
            )

        except Exception as e:
            raise

    def start_consuming(self) -> None:
        """메시지 소비를 시작합니다."""
        queue_name = self.config.get("queue_name")
        if not queue_name:
            raise ValueError("Queue name must be configured to start consuming")

        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
            except Exception as e:
                raise

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )

        self.channel.start_consuming()

    def close(self) -> None:
        """연결을 종료합니다."""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
