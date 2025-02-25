from typing import List, Optional

import pytest
from resque_api.application.ports.repository.exceptions import AggregateNotFoundError, DeleteNonExistentAggregateError
from resque_api.application.ports.repository.repository import Repository

class Entity:
    def __init__(self, id: int, data: str):
        self.id = id
        self.data = data

class FakeRepository(Repository):
    def __init__(self):
        self._entities = {}

    def _save(self, entity: Entity) -> None:
        self._entities[entity.id] = entity

    def _get(self, entity_id: int) -> Optional[Entity]:
        return self._entities.get(entity_id)

    def _find_all(self) -> List[Entity]:
        return list(self._entities.values())

    def _update(self, entity: Entity) -> None:
        if entity.id in self._entities:
            self._entities[entity.id] = entity

    def _delete(self, entity_id: int) -> None:
        if entity_id in self._entities:
            del self._entities[entity_id]

class TestCreateEntity:
    def test_create_new_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        assert any(e.id == 1 for e in repo._entities.values())

    def test_create_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        duplicate_entity = Entity(id=1, data="duplicate data")
        repo.save(duplicate_entity)
        assert any(e.id == 1 for e in repo._entities.values())

class TestReadEntity:
    def test_read_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        result = repo.get(1)
        assert result == entity

    def test_read_nonexistent_entity(self):
        repo = FakeRepository()
        with pytest.raises(AggregateNotFoundError):
            result = repo.get(999)    

class TestUpdateEntity:
    def test_update_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo._entities[entity.id] = entity
        updated_entity = Entity(id=1, data="updated data")
        repo.update(updated_entity)

        assert repo._entities[entity.id] == updated_entity
        
    def test_update_entity_no_change(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo._entities[entity.id] = entity
        updated_entity = Entity(id=1, data="updated data")
        repo.update(updated_entity)

class TestDeleteEntity:
    def test_delete_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo._entities[entity.id] = entity
        repo.delete(1)
        assert 1 not in repo._entities

    def test_delete_nonexistent_entity(self):
        repo = FakeRepository()
        with pytest.raises(DeleteNonExistentAggregateError):
            repo.delete(999)
        