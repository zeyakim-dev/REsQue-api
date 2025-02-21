class RequirementError(Exception):
    """요구사항 도메인 기본 예외"""

class InvalidStatusTransitionError(RequirementError):
    """잘못된 상태 전이 시도 예외"""

class RequirementPriorityError(RequirementError):
    """유효하지 않은 우선순위 값 예외"""

class DependencyCycleError(RequirementError):
    """의존성 순환 발생 예외"""

class TagLimitExceededError(RequirementError):
    """태그 개수 초과 예외"""

class RequirementTitleLengthError(RequirementError):
    """요구사항 제목 길이 예외"""
