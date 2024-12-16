from abc import ABC, abstractmethod
from signal import SIG_DFL
from typing import Generic, TypeVar

from src.application.message.command.command import Command
from src.application.ports.uow import UnitOfWork
from src.application.validation.validation_context import ValidationContext

C = TypeVar('C', bound=Command)
R = TypeVar('R')

class CommandHandler(Generic[C, R], ABC):
    """명령을 처리하는 추상 핸들러 클래스입니다.
    
    
    이 클래스는 CQRS 패턴에서 명령을 실행하고 관리하는 기본 구현을 제공합니다.
    제네릭 타입 C는 처리할 구체적인 명령의 타입을, R은 명령 실행 결과의 타입을 나타냅니다.
    각 핸들러는 이 클래스를 상속받아 execute와 _validate_command 메서드를 반드시 구현해야 합니다.
    명령의 유효성 검증은 ValidationContext를 통해 자동으로 관리되며, 모든 검증 오류는 일괄적으로 보고됩니다.


    Example:
        >>> # CreateUser 명령을 처리하는 핸들러 예시
        >>> class CreateUserHandler(CommandHandler[CreateUserCommand, str]):
        ...     def execute(self, command: CreateUserCommand, uow: UnitOfWork) -> str:
        ...         user_id = self._create_user(command)  # 사용자 생성 로직
        ...         return user_id
        ...     
        ...     def _validate_command(self, command: Command, context: ValidationContext):
        ...         Username.validate(context, command.username)  # 사용자명 검증
        ...         Email.validate(context, command.email)  # 이메일 검증

    Attributes:
        _validation_context: 명령의 유효성 검증을 수행하는 컨텍스트 객체
    """

    def __init__(self, validation_context: ValidationContext):
        """CommandHandler를 초기화합니다.

        ValidationContext를 주입받아 명령의 유효성 검증에 사용합니다.
        이 컨텍스트는 모든 검증 과정에서 재사용됩니다.

        Args:
            validation_context: 명령 유효성 검증을 수행할 컨텍스트 객체
        """
        self._validation_context = validation_context

    @abstractmethod
    def execute(self, command: C, uow: UnitOfWork) -> R:
        """명령을 실행하고 그 결과를 반환합니다.

        이 메서드는 실제 비즈니스 로직을 수행하며, Unit of Work 패턴을 통해
        트랜잭션 범위 내에서 모든 작업이 수행됨을 보장합니다.

        Args:
            command: 실행할 구체적인 명령 객체
            uow: 트랜잭션 처리를 위한 Unit of Work 객체

        Returns:
            명령 실행의 결과값. 반환 타입은 핸들러의 제네릭 타입 R에 의해 결정됩니다.

        Raises:
            NotImplementedError: 이 추상 메서드가 구현되지 않은 경우
        """
        raise NotImplementedError

    def validate_command(self, command: Command) -> None:
        """명령의 유효성을 검증합니다.

        컨텍스트 매니저를 사용하여 ValidationContext의 생명주기를 관리하며,
        검증 과정에서 발생하는 모든 오류를 수집합니다.

        Args:
            command: 검증할 명령 객체

        Raises:
            ValidationException: 하나 이상의 유효성 검증 규칙을 위반한 경우
        """
        with self._validation_context as context:
            self._validate_command(command, context)

    @abstractmethod
    def _validate_command(self, command: Command, context: ValidationContext) -> None:
        """명령 객체의 유효성을 검사하는 기본 메서드입니다.

        각각의 명령 핸들러는 이 메서드를 구현하여 자신만의 검증 규칙을 정의합니다.
        검증 과정에서 발견된 모든 오류는 ValidationContext를 통해 수집되며, 
        이는 나중에 한꺼번에 보고됩니다.

        예를 들어, 회원 가입 명령의 경우 사용자 이름, 비밀번호, 이메일 주소에 대한
        검증을 수행할 수 있습니다. 주문 생성 명령의 경우에는 주문 수량, 배송 주소 등을 
        검증할 수 있습니다.

        Args:
            command: 검증할 명령 객체. 각 핸들러는 자신이 처리하는 명령 타입에 맞는
                구체적인 검증을 수행해야 합니다.
            context: 검증 오류를 수집하는 컨텍스트 객체. 모든 검증 오류는 이 컨텍스트에
                기록되어야 합니다.
        """
        raise NotImplementedError
