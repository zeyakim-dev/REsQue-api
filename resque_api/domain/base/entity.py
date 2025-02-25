from abc import ABC
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

@dataclass(frozen=True, kw_only=True)
class Entity(ABC):
    id: UUID = field(default_factory=uuid4)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return self.id == other.id
