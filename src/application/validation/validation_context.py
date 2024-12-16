from typing import Dict, List, Optional, Type, TypeVar
from src.application.validation.exceptions import ValidationException
from src.domain.shared.base.value import Value
from src.domain.shared.domain_exception import ValueObjectValidationException

V = TypeVar('V', bound=Value)

class ValidationContext:
    """유효성 검증 컨텍스트를 관리하는 클래스입니다.

    이 클래스는 값 객체(Value Object)의 유효성 검증 과정에서 발생하는 오류들을 수집하고 관리합니다.
    컨텍스트 매니저 프로토콜을 구현하여 검증 과정의 생명주기를 자동으로 관리하며,
    검증 완료 시점에 수집된 모든 오류를 한 번에 보고할 수 있습니다.

    Attributes:
        errors (Dict[str, List[ValueObjectValidationException]]): 
            필드별 유효성 검증 오류를 저장하는 딕셔너리.
            키는 필드 이름이고 값은 해당 필드에서 발생한 오류들의 리스트입니다.
        _has_validation (bool): 
            유효성 검증이 수행되었는지를 나타내는 플래그.

    Example:
        >>> with ValidationContext() as context:
        ...     context.add_error("email", InvalidEmailFormatException("잘못된 이메일 형식"))
        ...     context.add_error("password", WeakPasswordException("비밀번호가 너무 짧습니다"))
        Traceback (most recent call last):
            ...
        ValidationException: {'email': [...], 'password': [...]}
    """

    def __init__(self):
        """ValidationContext 인스턴스를 초기화합니다."""
        self.errors: Dict[str, List[ValueObjectValidationException]] = {}
        self._has_validation = False

    def __enter__(self) -> 'ValidationContext':
        """컨텍스트 매니저 진입점입니다.

        Returns:
            ValidationContext: 현재 ValidationContext 인스턴스.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """컨텍스트 매니저 종료 시점에서 수집된 오류를 처리합니다.

        검증이 수행되었고 오류가 존재하는 경우 ValidationException을 발생시킵니다.
        종료 시 모든 오류를 자동으로 초기화합니다.

        Args:
            exc_type: 발생한 예외의 타입
            exc_val: 발생한 예외 인스턴스
            exc_tb: 예외의 트레이스백

        Returns:
            bool: 예외 처리 여부를 나타내는 불리언 값

        Raises:
            ValidationException: 유효성 검증 과정에서 오류가 발생한 경우
        """
        try:
            if self._has_validation and self.errors:
                raise ValidationException(self.errors)
        finally:
            self.errors.clear()

    def add_error(self, field_name: str, error: ValueObjectValidationException) -> None:
        """특정 필드의 유효성 검증 오류를 컨텍스트에 추가합니다.

        Args:
            field_name (str): 오류가 발생한 필드의 이름
            error (ValueObjectValidationException): 발생한 유효성 검증 오류

        Example:
            >>> context.add_error("email", InvalidEmailFormatException("잘못된 이메일 형식"))
        """
        if field_name not in self.errors:
            self.errors[field_name] = []
        self.errors[field_name].append(error)