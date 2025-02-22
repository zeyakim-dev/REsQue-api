from dataclasses import dataclass
from enum import Enum
from typing import Self

from resque_api.domain.base.value_object import ValueObject
from resque_api.domain.requirement.exceptions import InvalidStatusTransitionError, InvalidPriorityError, RequirementTitleLengthError, TagNotFoundError

@dataclass(frozen=True)
class RequirementTitle(ValueObject[str]):
    """요구사항 제목 VO (2~100자)"""

    value: str

    def __post_init__(self):
        if not (2 <= len(self.value) <= 100):
            raise RequirementTitleLengthError("제목은 2자 이상, 100자 이하여야 합니다.")


@dataclass(frozen=True)
class RequirementDescription(ValueObject[str]):
    """요구사항 설명 VO"""

    value: str

    def __post_init__(self):
        if len(self.value) < 5:
            raise ValueError("설명은 최소 5자 이상이어야 합니다.")


@dataclass(frozen=True)
class RequirementTags:
    """요구사항 태그 VO"""

    values: list[str]

    def __post_init__(self):
        self._validate_tags()

    def _validate_tags(self):
        """태그 정리 및 중복 제거"""
        object.__setattr__(self, "values", sorted(set(t.lower().strip() for t in self.values)))

    def add_tag(self, tag: str) -> Self:
        """태그 추가"""
        return RequirementTags(self.values + [tag])

    def remove_tag(self, tag: str) -> Self:
        """태그 제거"""
        normalized_tag = tag.strip().lower()
        if normalized_tag not in self.values:
            raise TagNotFoundError(f"Tag '{normalized_tag}' does not exist.")
        return RequirementTags([t for t in self.values if t != normalized_tag])


class RequirementStatusEnum(Enum):
    """요구사항 상태 Enum"""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@dataclass(frozen=True)
class RequirementStatus(ValueObject[RequirementStatusEnum]):
    """요구사항 상태 Value Object"""

    value: RequirementStatusEnum
    _VALID_TRANSITIONS = {
        RequirementStatusEnum.TODO: {RequirementStatusEnum.IN_PROGRESS},
        RequirementStatusEnum.IN_PROGRESS: {RequirementStatusEnum.TODO, RequirementStatusEnum.DONE},
        RequirementStatusEnum.DONE: set(),
    }


    def change_status(self, new_status: Self) -> Self:
        """요구사항 상태 변경 검증"""
        if new_status.value not in self._VALID_TRANSITIONS[self.value]:
            raise InvalidStatusTransitionError(
                f"상태를 '{self.value.value}'에서 '{new_status.value.value}'로 변경할 수 없습니다."
            )

        return RequirementStatus(new_status.value)

    def is_done(self) -> bool:
        """요구사항이 완료 상태인지 확인"""
        return self.value == RequirementStatusEnum.DONE

    def can_transition_to(self, new_status: Self) -> bool:
        """해당 상태로 전환이 가능한지 확인"""
        return new_status.value in self._VALID_TRANSITIONS[self.value]


@dataclass(frozen=True)
class RequirementPriority(ValueObject[int]):
    """요구사항 우선순위 값 객체 (1-3)"""

    value: int

    def __post_init__(self):
        if not 1 <= self.value <= 3:
            raise InvalidPriorityError("Priority must be between 1 and 3")