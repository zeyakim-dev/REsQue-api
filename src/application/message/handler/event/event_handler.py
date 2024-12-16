from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.application.message.event.event import Event
from src.application.ports.uow import UnitOfWork

E = TypeVar('E', bound=Event)

class EventHandler(Generic[E], ABC):
    @abstractmethod
    def handle(self, event: E, uow: UnitOfWork) -> None:
        ...