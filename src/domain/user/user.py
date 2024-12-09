from dataclasses import dataclass
from uuid import UUID

from src.domain.shared.aggregate_root import AggregateRoot
from src.domain.shared.entity import Entity
from src.domain.user.values import HashedPassword, Username


@dataclass(frozen=True)
class User(AggregateRoot):
    username: Username
    hashed_password: HashedPassword

    @classmethod
    def reconstitute(cls, id: UUID, username: str, hashed_password: str) -> "User":
        """저장소에서 엔티티를 재구성할 때 사용하는 팩토리 메서드"""
        return cls(
            id=id,
            username=Username(username),
            hashed_password=HashedPassword(hashed_password),
        )
