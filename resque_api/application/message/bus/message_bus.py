from typing import Type

from resque_api.application.message.command.base.command_handler import CommandHandler
from resque_api.application.message.common.message import Message
from resque_api.application.message.event.base.event_handler import EventHandler
from resque_api.application.ports.uow import UnitOfWork


class MessageBus:
    def __init__(self, uow: UnitOfWork):
        self.handlers: dict[Type[Message], CommandHandler | EventHandler] = dict()
        self.event_queue = []
        self.uow = uow

    def subscribe(self, handler: CommandHandler | EventHandler, message_type: Type[Message]):
        self.handlers[message_type] = handler

    def publish(self, message: Message):
        handler = self.handlers.get(type(message))
        
        if handler is None:
            raise Exception(f"등록된 핸들러가 없습니다. 메시지 타입: {type(message).__name__}")
        
        result = handler.handle(message, self.uow)
        events = self.uow.pop_events()

        if events:
            self.event_queue.extend(events)
        return result