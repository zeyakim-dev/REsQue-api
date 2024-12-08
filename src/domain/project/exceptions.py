from src.domain.domain_exception import DomainException


class ProjectDomainException(DomainException):
    """프로젝트 도메인과 관련된 모든 예외의 기본 클래스입니다."""

    pass


class InvalidTitleException(ProjectDomainException):
    """유효하지 않은 프로젝트 제목일 때 발생하는 예외입니다."""

    def __init__(self, title: str, reason: str):
        self.title = title
        super().__init__(
            f"유효하지 않은 프로젝트 제목입니다: '{title}'. " f"원인: {reason}"
        )


class InvalidDescriptionException(ProjectDomainException):
    """유효하지 않은 프로젝트 설명일 때 발생하는 예외입니다."""

    def __init__(self, reason: str):
        super().__init__(f"유효하지 않은 프로젝트 설명입니다. " f"원인: {reason}")


class InvalidStatusTransitionException(ProjectDomainException):
    """유효하지 않은 상태 전이를 시도할 때 발생하는 예외입니다."""

    def __init__(self, from_status: str, to_status: str):
        self.from_status = from_status
        self.to_status = to_status
        super().__init__(
            f"유효하지 않은 상태 전이입니다: '{from_status}'에서 '{to_status}'로 변경할 수 없습니다"
        )


class ProjectNotFoundException(ProjectDomainException):
    """프로젝트를 찾을 수 없을 때 발생하는 예외입니다."""

    def __init__(self, identifier: str):
        super().__init__(f"프로젝트를 찾을 수 없습니다: {identifier}")


class DuplicateProjectTitleException(ProjectDomainException):
    """이미 존재하는 프로젝트 제목으로 생성을 시도할 때 발생하는 예외입니다."""

    def __init__(self, title: str):
        super().__init__(f"이미 사용 중인 프로젝트 제목입니다: {title}")
