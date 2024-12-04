import dataclasses
from datetime import datetime
from uuid import UUID
import pytest
from src.domain.user.user import User, IdGenerator, PasswordHasher

class TestUser:
    def test_create_user(
        self,
        valid_user_info,
        password_hasher: PasswordHasher,
        id_generator: IdGenerator,
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

    def test_user_equality(self, valid_user_info, password_hasher, id_generator):
        # Given
        user1 = User.create(valid_user_info, password_hasher, id_generator)
        user2 = User.create(valid_user_info, password_hasher, id_generator)
        
        # Then
        assert user1 == user2