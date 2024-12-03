from typing import List, Protocol, Type, TypeVar

from src.application.events.event import Event
from src.application.ports.repositories.repository import Repository

T = TypeVar("T", bound="Repository")


class UnitOfWork(Protocol):
    def __enter__(self) -> "UnitOfWork": ...

    def __exit__(self, *args) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
    
    def collect_new_events(self) -> List[Event]: ...

    @property
    def get_repository(self, repository_type: Type[T]) -> T: ...
