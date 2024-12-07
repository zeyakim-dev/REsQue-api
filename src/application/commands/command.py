from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Generic, List, TypeVar

from src.application.ports.uow import UnitOfWork

T = TypeVar("T")


class Command(Generic[T], ABC):
    """모든 커맨드의 기본 클래스입니다.

    커맨드는 단일 비즈니스 작업을 캡슐화하며,
    UnitOfWork를 통해 트랜잭션 범위 내에서 실행됩니다.
    """
    @abstractmethod
    def get_validators(self) -> Dict[Any, List[Callable]]:
        """검증 규칙을 반환합니다."""
        pass

    def validate(self):
        """객체 생성 시 자동으로 모든 필드를 검증합니다"""
        validators = self.get_validators()
        for value, validator in validators.items():
            try:
                validator(value)
            except ValueError as e:
                # 도메인 특화된 예외로 변환
                raise ValueError(
                    validator.__name__.replace('validate_', ''),
                    str(e)
                )


    def __post_init__(self):
        """dataclass 생성 후 자동으로 검증을 수행합니다."""
        self.validate()

    @abstractmethod
    def execute(self, uow: UnitOfWork) -> T:
        """커맨드를 실행하고 결과를 반환합니다.

        모든 데이터베이스 작업은 제공된 UnitOfWork의 트랜잭션 내에서 실행됩니다.
        """
        pass
