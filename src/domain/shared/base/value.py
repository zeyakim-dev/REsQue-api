from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class Value(Protocol):
    pass