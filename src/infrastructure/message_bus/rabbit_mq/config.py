from dataclasses import dataclass
from typing import Optional

from src.infrastructure.message_bus.rabbit_mq.rabbit_mq_message_bus import RabbitMQMessageBus

def create_rabbitmq_message_bus(config: dict, command_handlers, event_handlers) -> RabbitMQMessageBus:
    return RabbitMQMessageBus(
        config=config,
        command_handlers=command_handlers,
        event_handlers=event_handlers
    )