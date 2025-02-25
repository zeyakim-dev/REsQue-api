from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol
from uuid import UUID, uuid4

@dataclass(frozen=True, kw_only=True)
class Message(Protocol):
    id: UUID = field(default_factory=uuid4)
    occured_at: datetime = field(default_factory=datetime.utcnow())
    