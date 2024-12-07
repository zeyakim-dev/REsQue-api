import dataclasses
from uuid import UUID

import pytest

from src.domain.user.user import User
from src.domain.user.values import HashedPassword, Username


class TestUser:
    def test_create_user(self):
        """User 엔티티가 올바르게 생성되는지 검증합니다."""
        # Given
        id = UUID("12345678-1234-5678-1234-567812345678")
        username = Username("testuser")
        hashed_password = HashedPassword("hashed_value")

        # When
        user = User(id=id, username=username, hashed_password=hashed_password)

        # Then
        assert user.id == id
        assert user.username == username
        assert user.hashed_password == hashed_password

    def test_user_is_immutable(self):
        """User 엔티티가 불변인지 검증합니다."""
        # Given
        user = User(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            username=Username("testuser"),
            hashed_password=HashedPassword("hashed_value"),
        )

        # When/Then
        with pytest.raises(dataclasses.FrozenInstanceError):
            user.username = Username("newname")

    def test_user_equality(self):
        """동일한 ID를 가진 User 엔티티가 동등한지 검증합니다."""
        # Given
        id = UUID("12345678-1234-5678-1234-567812345678")
        user1 = User(
            id=id,
            username=Username("testuser"),
            hashed_password=HashedPassword("hashed_value"),
        )
        user2 = User(
            id=id,
            username=Username("testuser"),
            hashed_password=HashedPassword("hashed_value"),
        )

        # Then
        assert user1 == user2
