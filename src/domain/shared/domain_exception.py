from typing import Generic, TypeVar
from src.domain.shared.base.aggregate import Aggregate

A = TypeVar("A", bound=Aggregate)

class DomainException(Exception):
    """도메인 계층의 모든 예외의 기본 클래스입니다."""
    def __init__(self, message: str):
        super().__init__(message)

class ValueObjectValidationException(DomainException, Generic[A]):
    """값 객체의 생성이나 수정 시 도메인 규칙 위반으로 발생하는 예외입니다."""
    def __init__(self, value_object_name: str, value: str, reason: str):
        message = f"{value_object_name} 유효성 검증 실패: '{value}'. {reason}"
        super().__init__(message)

class BusinessRuleViolationException(DomainException, Generic[A]):
    """도메인의 비즈니스 규칙이 위반되었을 때 발생하는 예외입니다."""
    def __init__(self, rule: str, reason: str):
        message = f"비즈니스 규칙 위반: {rule}. {reason}"
        super().__init__(message)

class InvalidStateTransitionException(DomainException, Generic[A]):
    """애그리게잇의 상태 변경이 허용되지 않을 때 발생하는 예외입니다."""
    def __init__(self, current_state: str, target_state: str, reason: str):
        message = f"잘못된 상태 전이: '{current_state}'에서 '{target_state}'로 전환 불가. {reason}"
        super().__init__(message)

class DomainInvariantViolationException(DomainException, Generic[A]):
    """도메인 모델의 핵심 불변식이 위반되었을 때 발생하는 예외입니다."""
    def __init__(self, invariant: str, reason: str):
        message = f"도메인 불변식 위반: {invariant}. {reason}"
        super().__init__(message)