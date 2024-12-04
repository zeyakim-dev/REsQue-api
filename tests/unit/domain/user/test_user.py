import dataclasses
from datetime import datetime
from uuid import UUID
import pytest
from src.domain.user.user import User

class StubPasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed_{password}"
        
    def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed_{password}"

class StubIdGenerator:
    def __init__(self, fixed_uuid: str = "01937b5c-7757-7855-8138-355fc7d85155"):
        self._uuid = UUID(fixed_uuid)
        
    def generate(self) -> UUID:
        return self._uuid

class TestUser:
    @pytest.fixture
    def password_hasher(self):
        return StubPasswordHasher()
        
    @pytest.fixture
    def id_generator(self):
        return StubIdGenerator()
        
    @pytest.fixture
    def valid_user_info(self):
        return {"username": "testuser", "password": "password123"}

    def test_create_user(
        self,
        valid_user_info,
        password_hasher: StubPasswordHasher,
        id_generator: StubIdGenerator,
    ):
        # When
        user = User.create(valid_user_info, password_hasher, id_generator)
        
        # Then
        assert user.username == valid_user_info["username"]
        assert user.hashed_password == f"hashed_{valid_user_info['password']}"
        assert user.id == id_generator.generate()

    def test_user_is_immutable(self, valid_user_info, password_hasher, id_generator):
        # Given
        user = User.create(valid_user_info, password_hasher, id_generator)
        
        # When/Then
        with pytest.raises(dataclasses.FrozenInstanceError):
            user.username = "new_username"

    def test_verify_password_success(
        self, valid_user_info, password_hasher, id_generator
    ):
        # Given
        user = User.create(valid_user_info, password_hasher, id_generator)
        
        # When
        result = user.verify_password(valid_user_info["password"], password_hasher)
        
        # Then
        assert result is True

    def test_verify_password_failure(
        self, valid_user_info, password_hasher, id_generator
    ):
        # Given
        user = User.create(valid_user_info, password_hasher, id_generator)
        
        # When
        result = user.verify_password("wrong_password", password_hasher)
        
        # Then
        assert result is False

    def test_create_user_with_different_id(self, valid_user_info, password_hasher):
        # Given
        different_uuid = "01937b64-4565-7865-8261-6d0cf7847b33"
        different_id_generator = StubIdGenerator(different_uuid)
        
        # When
        user = User.create(valid_user_info, password_hasher, different_id_generator)
        
        # Then
        assert user.id == UUID(different_uuid)

    def test_user_equality(self, valid_user_info, password_hasher, id_generator):
        # Given
        user1 = User.create(valid_user_info, password_hasher, id_generator)
        user2 = User.create(valid_user_info, password_hasher, id_generator)
        
        # Then
        assert user1 == user2