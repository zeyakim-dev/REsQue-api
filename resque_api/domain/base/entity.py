from abc import ABC
from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class Entity(ABC):
    id: UUID = field(default_factory=uuid4)
