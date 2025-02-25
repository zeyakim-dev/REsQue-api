from dataclasses import dataclass
from datetime import datetime
from typing import Type

from resque_api.domain.base.aggregate import Aggregate

@dataclass
class EventSnapshot:
    snapshot_id: int
    aggregate_id: int
    aggregate_type: Type[Aggregate]
    version: int
    timestamp: datetime
    state: Aggregate
