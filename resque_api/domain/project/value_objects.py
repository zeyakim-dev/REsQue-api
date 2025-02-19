from dataclasses import dataclass
from datetime import datetime
from enum import Enum

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

@dataclass(frozen=True)
class ProjectMember:
    """프로젝트 멤버 값 객체"""
    user: 'User'  # type: ignore
    role: ProjectRole

@dataclass(frozen=True)
class ProjectInvitation:
    """프로젝트 초대 값 객체"""
    email: str
    role: ProjectRole
    expires_at: datetime
    code: str
    status: InvitationStatus = InvitationStatus.PENDING
