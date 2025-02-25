from datetime import datetime
from typing import Protocol, Type
from uuid import UUID

from resque_api.application.message.event.base.event import Event
from resque_api.application.message.event_store.event_snapshot import EventSnapshot
from resque_api.application.message.event_store.stored_event import StoredEvent
from resque_api.domain.base.aggregate import Aggregate


class EventStore(Protocol):
    def __init__(self):
        ...

    def get_latest_snapshot(self, aggregate_id: UUID, aggregate_type: Type[Aggregate]) -> EventSnapshot:
        """가장 최근에 저장된 애그리게이트 스냅샷을 반환합니다."""
        ...

    def get_events(self, snapshot: EventSnapshot, date: datetime | None = None) -> list[Event]:
        """지정된 시간 범위 내의 모든 이벤트를 반환합니다."""
        if date is None:
            date = datetime.now()
        stored_events = self._get_events(snapshot, date)
        return [stored_event.event for stored_event in stored_events]

    def _get_events(self, snapshot: EventSnapshot, date: datetime) -> list[StoredEvent]:
        ...

    def save(self, event: Event):
        stored_event = StoredEvent(
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            version=event.version,
            timestamp=event.timestamp,
            event=event
        )
        self._save(stored_event)

    def _save(self, stored_event: StoredEvent):
        ...
