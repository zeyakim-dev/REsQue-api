from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.application.ports.uow import UnitOfWork

T = TypeVar("T")


class Command(Generic[T], ABC):
    """모든 커맨드의 기본 클래스입니다.

    커맨드는 단일 비즈니스 작업을 캡슐화하며,
    UnitOfWork를 통해 트랜잭션 범위 내에서 실행됩니다.
    """

    @abstractmethod
    def execute(self, uow: UnitOfWork) -> T:
        """커맨드를 실행하고 결과를 반환합니다.

        모든 데이터베이스 작업은 제공된 UnitOfWork의 트랜잭션 내에서 실행됩니다.
        """
        pass
