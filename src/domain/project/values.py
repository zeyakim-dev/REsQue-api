from dataclasses import dataclass
from enum import Enum
from typing import List

from src.domain.project.exceptions import (
    InvalidDescriptionException,
    InvalidStatusTransitionException,
    InvalidTitleException,
)


@dataclass(frozen=True)
class Title:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise InvalidTitleException(self.value, "제목은 문자열이어야 합니다")

        if not self.value.strip():
            raise InvalidTitleException(self.value, "제목은 비어있을 수 없습니다")

        if len(self.value) > 100:
            raise InvalidTitleException(
                self.value, "제목은 최대 100자까지만 가능합니다"
            )

        if len(self.value.strip()) < 2:
            raise InvalidTitleException(self.value, "제목은 최소 2자 이상이어야 합니다")


@dataclass(frozen=True)
class Description:
    value: str

    def __post_init__(self):
        if not isinstance(self.value, str):
            raise InvalidDescriptionException("설명은 문자열이어야 합니다")

        if len(self.value) > 1000:
            raise InvalidDescriptionException("설명은 최대 1000자까지만 가능합니다")


class Status(Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

    @classmethod
    def can_transition(cls, from_status: "Status", to_status: "Status") -> bool:
        valid_transitions = {
            cls.DRAFT: [cls.IN_PROGRESS],
            cls.IN_PROGRESS: [cls.DONE],
            cls.DONE: [],
        }
        return to_status in valid_transitions.get(from_status, [])

    def transition_to(self, new_status: "Status") -> "Status":
        if not self.can_transition(self, new_status):
            raise InvalidStatusTransitionException(self.value, new_status.value)
        return new_status
