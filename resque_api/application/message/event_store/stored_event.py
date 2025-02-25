from dataclasses import dataclass
from datetime import datetime
from typing import Type
from uuid import UUID

from resque_api.application.message.event.base.event import Event
from resque_api.domain.base.aggregate import Aggregate

@dataclass
class StoredEvent:
    id: UUID
    aggregate_type: Type[Aggregate]
    aggregate_id: UUID
    version: int
    timestamp: datetime
    event: Event
