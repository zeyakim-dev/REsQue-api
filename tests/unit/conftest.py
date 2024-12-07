from uuid import UUID

import pytest


class StubPasswordHasher:
    """테스트용 PasswordHasher Stub"""

    def hash(self, password: str) -> str:
        return f"hashed_{password}"

    def verify(self, password: str, hashed_password: str) -> bool:
        return hashed_password == f"hashed_{password}"


class StubIdGenerator:
    """테스트용 IdGenerator Stub"""

    def __init__(self, fixed_uuid: str = "01937b5c-7757-7855-8138-355fc7d85155"):
        self._uuid = UUID(fixed_uuid)

    def generate(self) -> UUID:
        return self._uuid


@pytest.fixture
def password_hasher():
    """PasswordHasher Stub fixture"""
    return StubPasswordHasher()


@pytest.fixture
def id_generator():
    """IdGenerator Stub fixture"""
    return StubIdGenerator()


@pytest.fixture
def different_id_generator():
    """다른 UUID를 생성하는 IdGenerator Stub fixture"""
    return StubIdGenerator("01937b64-4565-7865-8261-6d0cf7847b33")


@pytest.fixture
def valid_user_info():
    """테스트용 유효한 사용자 정보"""
    return {"username": "testuser", "password": "password123"}
