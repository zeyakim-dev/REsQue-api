from abc import ABC, abstractmethod
from typing import List, Type, TypeVar

from src.application.events.event import Event
from src.application.ports.repositories.repository import Repository

T = TypeVar("T", bound="Repository")


class UnitOfWork(ABC):
    """Unit of Work 추상 기본 클래스"""

    def __init__(self):
        self.events: List[Event] = []

    def __enter__(self) -> "UnitOfWork":
        """Unit of Work 컨텍스트를 시작합니다."""
        try:
            return self._begin()
        except Exception:
            self._rollback()
            raise

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        """Unit of Work 컨텍스트를 종료합니다."""
        if exc_type is None:
            self._commit()
        else:
            self._rollback()

    def _begin(self) -> "UnitOfWork":
        """UnitOfWork 작업을 시작합니다."""
        return self

    @abstractmethod
    def _commit(self) -> None:
        """현재 작업을 커밋합니다."""
        ...

    @abstractmethod
    def _rollback(self) -> None:
        """현재 작업을 롤백합니다."""
        ...

    @abstractmethod
    def get_repository(self, repository_type: Type[T]) -> T:
        """요청된 타입의 레포지토리를 반환합니다."""
        ...

    def collect_new_events(self) -> List[Event]:
        """수집된 이벤트를 반환하고 초기화합니다."""
        events = self.events
        self.events = []
        return events

    def add_event(self, event: Event) -> None:
        """새로운 이벤트를 추가합니다."""
        self.events.append(event)
