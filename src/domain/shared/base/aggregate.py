from dataclasses import dataclass
from src.domain.shared.base.entity import Entity

@dataclass(frozen=True)
class Aggregate(Entity):
    pass