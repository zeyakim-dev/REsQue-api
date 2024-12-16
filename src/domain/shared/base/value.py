from abc import ABC, abstractmethod
from dataclasses import dataclass
import re
from typing import Any, ClassVar

from src.application.validation.validation_context import ValidationContext
from src.domain.shared.domain_exception import ValueObjectValidationException


@dataclass(frozen=True)
class Value(ABC):
    """값 객체(Value Object)의 기본 클래스를 정의합니다.

    이 추상 클래스는 모든 값 객체의 기반이 되며, 자동 필드명 생성과 유효성 검증을 위한 
    공통 기능을 제공합니다. 값 객체는 불변성을 보장하기 위해 frozen=True로 설정됩니다.

    클래스 속성:
        _field_name (ClassVar[str]): 값 객체의 필드명을 저장합니다. 클래스명을 snake_case로 
            자동 변환하여 생성됩니다. 예를 들어 'UserName' 클래스는 'user_name'이 됩니다.

    예시:
        >>> class UserName(Value):
        ...     value: str
        ...     def _validate(cls, value: str) -> None:
        ...         if len(value) < 3:
        ...             raise ValueObjectValidationException("사용자명이 너무 짧습니다")
        >>> UserName.field_name()
        'user_name'
    """

    _field_name: ClassVar[str] = ''
    
    @classmethod
    def field_name(cls) -> str:
        """값 객체의 필드명을 반환합니다.

        Returns:
            str: snake_case 형식의 필드명

        Example:
            >>> EmailAddress.field_name()
            'email_address'
        """
        return cls._field_name
    
    def __init_subclass__(cls, **kwargs):
        """하위 클래스가 생성될 때 자동으로 호출되어 필드명을 생성합니다.

        클래스명을 snake_case로 변환하여 _field_name에 저장합니다.
        예를 들어 'EmailAddress'는 'email_address'가 됩니다.

        Args:
            **kwargs: 상위 클래스로 전달할 추가 인자들
        """
        super().__init_subclass__(**kwargs)
        name = re.sub('([A-Z])', r'_\1', cls.__name__).lower().lstrip('_')
        cls._field_name = name

    @classmethod
    def validate(cls, context: ValidationContext, value: Any) -> None:
        """값의 유효성을 검증하고 오류가 있다면 컨텍스트에 기록합니다.

        이 메서드는 _validate 메서드를 호출하여 실제 검증을 수행하고,
        오류가 발생하면 ValidationContext에 해당 오류를 추가합니다.

        Args:
            context (ValidationContext): 유효성 검증 오류를 수집하는 컨텍스트
            value (Any): 검증할 값

        Example:
            >>> with ValidationContext() as context:
            ...     UserName.validate(context, "ab")  # 너무 짧은 이름
            >>> context.errors
            {'user_name': [ValueObjectValidationException("사용자명이 너무 짧습니다")]}
        """
        try:
            cls._validate(value)
        except ValueObjectValidationException as e:
            context.add_error(cls._field_name, e)

    @classmethod
    @abstractmethod
    def _validate(self, value: Any) -> None:
        """값의 유효성을 검증하는 실제 로직을 구현합니다.
    
        이 추상 메서드는 모든 하위 클래스에서 반드시 구현해야 합니다.
        유효성 검증에 실패하면 ValueObjectValidationException을 발생시켜야 합니다.
    
        Args:
            value (Any): 검증할 값
    
        Raises:
            ValueObjectValidationException: 유효성 검증에 실패한 경우
            NotImplementedError: 하위 클래스에서 이 메서드를 구현하지 않은 경우
        """
        raise NotImplementedError