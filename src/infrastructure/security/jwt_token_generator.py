from datetime import datetime, timedelta
from typing import Dict

import jwt


class JWTTokenGenerator:
    """JWT 토큰 생성기입니다."""

    def __init__(self, secret_key: str, token_expiry_minutes: int):
        self._secret_key = secret_key
        self._token_expiry_minutes = token_expiry_minutes

    def generate_token(self, payload: Dict) -> str:
        """JWT 토큰을 생성합니다.

        Args:
            payload: 토큰에 포함될 데이터

        Returns:
            str: 생성된 JWT 토큰
        """
        token_data = payload.copy()
        expire = datetime.utcnow() + timedelta(minutes=self._token_expiry_minutes)

        token_data.update({"exp": expire, "iat": datetime.utcnow()})

        return jwt.encode(token_data, self._secret_key, algorithm="HS256")
