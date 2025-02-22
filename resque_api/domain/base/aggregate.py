from dataclasses import dataclass

from resque_api.domain.base.entity import Entity


@dataclass(frozen=True)
class Aggregate(Entity):
    ...
