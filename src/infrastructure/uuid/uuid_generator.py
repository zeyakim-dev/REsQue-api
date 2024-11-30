import random
import time
from uuid import UUID


class UUIDv7Generator:
    def generate(self) -> UUID:
        timestamp_ms = int(time.time() * 1000)
        uuid_int = (timestamp_ms << 80) | (random.getrandbits(80))
        uuid_int &= ~(0xF000 << 48)
        uuid_int |= 0x7000 << 48
        uuid_int &= ~(0xC0 << 56)
        uuid_int |= 0x80 << 56

        return UUID(int=uuid_int)
