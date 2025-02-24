from typing import Any, Generic, Protocol, TypeVar

from resque_api.application.message.event.base.event import Event
from resque_api.application.ports.uow import UnitOfWork

E = TypeVar('E', bound=Event)

class EventHandler(Protocol, Generic[E]):
    def handle(self, event: E, uow: UnitOfWork) -> None:
        ...