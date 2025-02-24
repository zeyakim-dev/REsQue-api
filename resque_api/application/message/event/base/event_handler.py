from typing import Any, Generic, Protocol, TypeVar

from resque_api.application.message.event.base.event import Event

E = TypeVar('E', bound=Event)

class EventHandler(Protocol, Generic[E]):
    def execute(self, event: E) -> None:
        ...