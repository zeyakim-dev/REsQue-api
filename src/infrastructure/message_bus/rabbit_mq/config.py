from dataclasses import dataclass
from typing import Optional

@dataclass
class RabbitMQConfig:
    host: str = 'localhost'
    port: int = 5672
    username: str = 'guest'
    password: str = 'guest'
    exchange_name: str = 'domain_events'
    queue_name: Optional[str] = None
    