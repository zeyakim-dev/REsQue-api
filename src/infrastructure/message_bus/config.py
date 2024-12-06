from typing import Any, Dict, List

from src.application.ports.message_bus import AbstractMessageBus
from src.infrastructure.message_bus.rabbit_mq.config import create_rabbitmq_message_bus


class MessageBusFactory:
    message_bus_factory = {
        'rabbitmq': create_rabbitmq_message_bus
    }
    
    @classmethod
    def create_message_bus(
        cls,
        configuration: Dict[str, Any],
        command_handlers: Dict[str, Any],
        event_handlers: Dict[str, List[Any]]
    ) -> AbstractMessageBus:
        message_bus_section = configuration['message_bus']
        message_bus_type = message_bus_section['type']
        message_bus_config = message_bus_section['config']

        creator = cls.message_bus_factory.get(message_bus_type)
        if not creator:
            raise ValueError(f"Unsupported message bus type: {message_bus_type}")

        return creator(
            config=message_bus_config,
            command_handlers=command_handlers,
            event_handlers=event_handlers
        )
