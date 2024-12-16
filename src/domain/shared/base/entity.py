from abc import ABC
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class Entity(ABC):
    id: UUID
