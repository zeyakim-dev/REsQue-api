from enum import Enum
from typing import Self

from resque_api.domain.requirement.exceptions import InvalidStatusTransitionError

VALID_TRANSITIONS = {
    "TODO": {"IN_PROGRESS"},
    "IN_PROGRESS": {"TODO", "DONE"},
    "DONE": set(),
}

class RequirementStatus(Enum):
    """요구사항 상태 값 객체"""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

    def change_status(self, new_status: Self) -> Self:
        """요구사항 상태 변경"""
        if not new_status.value in VALID_TRANSITIONS[self.value]:
            raise InvalidStatusTransitionError(
                f"상태를 '{self.value}'에서 '{new_status.value}'로 변경할 수 없습니다."
            )

        return new_status


class RequirementPriority(int):
    """요구사항 우선순위 값 객체 (1-3)"""
    def __new__(cls, value):
        if not 1 <= value <= 3:
            raise ValueError("Priority must be between 1 and 3")
        return super().__new__(cls, value)
