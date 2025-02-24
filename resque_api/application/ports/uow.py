from typing import Protocol, Optional, Self, Type, Any

from resque_api.application.message.event.base.event import Event


class UnitOfWork(Protocol):
    def __init__(self):
        self.events = []

    def __enter__(self) -> Self:
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_value: Optional[BaseException],
                 tb: Optional[Any]) -> None:
        if exc_type is None:
            self.commit()
        else:
            self.rollback()

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def publish(self, event: Event):
        self.events.append(event)

    def pop_events(self) -> tuple[Event, ...]:
        events = tuple(self.events)
        self.events.clear()
        return events
