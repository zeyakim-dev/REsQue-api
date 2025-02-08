from enum import Enum

class AuthProvider(Enum):
    """인증 제공자"""
    EMAIL = "EMAIL"
    GOOGLE = "GOOGLE"

class UserStatus(Enum):
    """사용자 상태"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE" 