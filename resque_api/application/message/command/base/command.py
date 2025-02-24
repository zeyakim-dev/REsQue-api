from dataclasses import dataclass
from resque_api.application.message.common.message import Message

@dataclass
class Command(Message):
    ...