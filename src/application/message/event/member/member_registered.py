from dataclasses import dataclass
from uuid import UUID

from src.application.message.event.event import Event
from src.application.ports.repositories.member.member_repository import MemberRepository


@dataclass(frozen=True)
class MemberRegisteredEvent(Event):
    ...