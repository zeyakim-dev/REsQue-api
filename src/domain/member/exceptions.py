from typing import Generic
from src.domain.member.entity.member import Member
from src.domain.shared.domain_exception import (
    ValueObjectValidationException,
    BusinessRuleViolationException
)

# 값 객체 유효성 검증 예외들
class InvalidUsernameException(ValueObjectValidationException[Member]):
    """Username 값 객체 생성 시 도메인 규칙 위반으로 발생하는 예외입니다.

    이 예외는 다음과 같은 상황에서 발생할 수 있습니다:
    - 길이 제한 위반 (최소 3자, 최대 20자)
    - 허용되지 않는 문자 포함 (특수문자, 공백)
    - 시스템 예약어 사용 (admin, system, root 등)"""

    def __init__(self, username: str, reason: str):
        super().__init__("사용자명", username, reason)

class InvalidPlainPasswordException(ValueObjectValidationException[Member]):
    """PlainPassword 값 객체 생성 시 보안 정책 위반으로 발생하는 예외입니다.

    이 예외는 다음과 같은 상황에서 발생할 수 있습니다:
    - 길이가 최소 요구사항 미달 (8자 미만)
    - 필수 문자 조합 누락 (영문 대소문자/숫자/특수문자)
    - 기타 보안 정책 위반 (연속된 문자, 사용자명 포함 등)"""

    def __init__(self, reason: str):
        super().__init__("비밀번호", "**********", reason)

class InvalidEmailException(ValueObjectValidationException[Member]):
    """Email 값 객체 생성 시 형식 검증 실패로 발생하는 예외입니다.

    이 예외는 다음과 같은 상황에서 발생할 수 있습니다:
    - 이메일 형식이 올바르지 않은 경우
    - 도메인 부분이 유효하지 않은 경우
    - 최대 길이 초과 (254자)"""

    def __init__(self, email: str, reason: str):
        super().__init__("이메일", email, reason)

class InvalidHashedPasswordException(ValueObjectValidationException[Member]):
    """HashedPassword 값 객체 생성 시 발생하는 예외입니다.

    이 예외는 다음과 같은 상황에서 발생할 수 있습니다:
    - 해시된 비밀번호의 형식이 올바르지 않은 경우
    - 해시 알고리즘 식별자가 누락된 경우"""

    def __init__(self, reason: str):
        super().__init__("해시된 비밀번호", "**********", reason)

# 비즈니스 규칙 위반 예외들
class DuplicateUsernameException(BusinessRuleViolationException[Member]):
    """회원 가입 시 이미 사용 중인 사용자명으로 인해 발생하는 예외입니다.

    이 예외는 새로운 회원을 등록할 때 사용자명 중복 검사 과정에서 발생합니다."""

    def __init__(self, username: str):
        super().__init__(
            "사용자명 중복",
            f"이미 사용 중인 사용자명입니다: {username}"
        )

class DuplicateEmailException(BusinessRuleViolationException[Member]):
    """회원 가입 시 이미 등록된 이메일 주소로 인해 발생하는 예외입니다.

    이 예외는 새로운 회원을 등록할 때 이메일 중복 검사 과정에서 발생합니다."""

    def __init__(self, email: str):
        super().__init__(
            "이메일 중복",
            f"이미 등록된 이메일 주소입니다: {email}"
        )

class MemberNotFoundException(BusinessRuleViolationException[Member]):
    """요청한 회원을 찾을 수 없을 때 발생하는 예외입니다.

    이 예외는 회원 ID나 사용자명으로 회원을 조회할 때 발생할 수 있습니다."""

    def __init__(self, identifier: str):
        super().__init__(
            "회원 조회 실패",
            f"해당 식별자로 회원을 찾을 수 없습니다: {identifier}"
        )