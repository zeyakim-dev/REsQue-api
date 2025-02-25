from typing import List, Optional
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
        assert repo.find_by_id(1) == entity

    def test_create_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        duplicate_entity = Entity(id=1, data="duplicate data")
        repo.save(duplicate_entity)
        assert repo.find_by_id(1) == duplicate_entity

class TestReadEntity:
    def test_read_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        result = repo.find_by_id(1)
        assert result == entity

    def test_read_nonexistent_entity(self):
        repo = FakeRepository()
        result = repo.find_by_id(999)
        assert result is None

class TestUpdateEntity:
    def test_update_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        updated_entity = Entity(id=1, data="updated data")
        repo.update(updated_entity)
        assert repo.find_by_id(1) == updated_entity

    def test_update_entity_no_change(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        unchanged_entity = Entity(id=1, data="test data")
        repo.update(unchanged_entity)
        assert repo.find_by_id(1) == entity

class TestDeleteEntity:
    def test_delete_existing_entity(self):
        repo = FakeRepository()
        entity = Entity(id=1, data="test data")
        repo.save(entity)
        repo.delete(1)
        assert repo.find_by_id(1) is None

    def test_delete_nonexistent_entity(self):
        repo = FakeRepository()
        repo.delete(999)
        assert repo.find_by_id(999) is None