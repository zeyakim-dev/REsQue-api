from enum import Enum

class RequirementStatus(Enum):
    """요구사항 상태 값 객체"""
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"

class RequirementPriority(int):
    """요구사항 우선순위 값 객체 (1-3)"""
    def __new__(cls, value):
        if not 1 <= value <= 3:
            raise ValueError("Priority must be between 1 and 3")
        return super().__new__(cls, value)
