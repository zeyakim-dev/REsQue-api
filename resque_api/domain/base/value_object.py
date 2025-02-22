from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class ValueObject:
    value: Any

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ValueObject):
            return NotImplemented
        return self.value == other.value
