from datetime import datetime, timedelta
import jwt
from typing import Dict

class JWTTokenGenerator:
    """JWT 토큰 생성기입니다."""
    
    def __init__(self, secret_key: str, token_expiry: timedelta):
        self._secret_key = secret_key
        self._token_expiry = token_expiry
        
    def generate_token(self, payload: Dict) -> str:
        """JWT 토큰을 생성합니다.
        
        Args:
            payload: 토큰에 포함될 데이터
            
        Returns:
            str: 생성된 JWT 토큰
        """
        token_data = payload.copy()
        expire = datetime.utcnow() + self._token_expiry
        
        token_data.update({
            "exp": expire,
            "iat": datetime.utcnow()
        })
        
        return jwt.encode(token_data, self._secret_key, algorithm="HS256")