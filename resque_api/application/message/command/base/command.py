from dataclasses import dataclass
from resque_api.application.message.common.message import Message

@dataclass(frozen=True, kw_only=True)
class Command(Message):
    ...