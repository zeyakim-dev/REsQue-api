from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from resque_api.domain.user.entities import User

class ProjectStatus(Enum):
    """프로젝트 상태"""
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"

class ProjectRole(Enum):
    """프로젝트 멤버 역할"""
    MANAGER = "MANAGER"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"

class InvitationStatus(Enum):
    """초대 상태"""
    PENDING = "PENDING"    # 초대 발송 후 대기 중
    ACCEPTED = "ACCEPTED"  # 초대 수락 완료
    EXPIRED = "EXPIRED"    # 초대 만료
    REVOKED = "REVOKED"    # 초대 취소
