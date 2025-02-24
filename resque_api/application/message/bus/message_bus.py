from typing import Type

from resque_api.application.message.command.base.command_handler import CommandHandler
from resque_api.application.message.common.message import Message
from resque_api.application.message.event.base.event_handler import EventHandler


class MessageBus:
    def __init__(self):
        self.handlers: dict[Type[Message], CommandHandler | EventHandler] = dict()
        self.event_queue = []

    def subscribe(self, handler: CommandHandler | EventHandler, message_type: Type[Message]):
        self.handlers[message_type] = handler

    def publish(self, message: Message):
        handler = self.handlers.get(type(message))
        
        if not handler:
            raise Exception
        return handler.handle(message)
