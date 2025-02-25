from typing import Protocol
from resque_api.application.ports.repository.exceptions import AggregateNotFoundError, DeleteNonExistentAggregateError
from resque_api.domain.base.aggregate import Aggregate


class Repository(Protocol):
    def save(self, aggregate: Aggregate) -> None:
        self._save(aggregate)

    def get(self, aggregate_id: str) -> Aggregate | None:
        aggregate = self._get(aggregate_id)
        if not aggregate:
            raise AggregateNotFoundError(f"{aggregate_id} not found")
        return aggregate

    def find_all(self) -> list[Aggregate]:
        return self._find_all()
    
    def update(self, aggregate: Aggregate) -> None:
        self._update(aggregate)

    def delete(self, aggregate_id: str) -> None:
        if not self._get(aggregate_id):
            raise DeleteNonExistentAggregateError(f"{aggregate_id} not found")
        self._delete(aggregate_id)

    def _save(self, aggregate: Aggregate) -> None:
        ...

    def _get(self, aggregate_id: str) -> Aggregate | None:  
        ...

    def _find_all(self) -> list[Aggregate]:
        ...

    def _update(self, aggregate: Aggregate) -> None:
        ...

    def _delete(self, aggregate_id: str) -> None:
        ...
