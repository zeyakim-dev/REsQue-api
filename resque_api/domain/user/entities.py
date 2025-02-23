import re
from dataclasses import dataclass, replace
from datetime import datetime
from uuid import UUID

from resque_api.domain.base.aggregate import Aggregate
from resque_api.domain.common.value_objects import Email
from resque_api.domain.user.exceptions import InactiveUserError
from resque_api.domain.user.value_objects import AuthProvider, Password, UserStatus


@dataclass(frozen=True)
class User(Aggregate):
    """사용자 엔티티 (Aggregate Root)"""

    email: Email
    auth_provider: AuthProvider
    status: UserStatus
    created_at: datetime
    password: Password = None

    def can_authenticate(self) -> bool:
        """인증 가능 여부 확인"""
        if self.status == UserStatus.INACTIVE:
            raise InactiveUserError("Inactive user cannot perform actions")

        if self.auth_provider != AuthProvider.EMAIL:
            return False

        return self.password is not None

    def update_status(self, new_status: UserStatus) -> "User":
        """사용자 상태 변경"""
        if self.status == UserStatus.INACTIVE:
            raise InactiveUserError("Inactive user cannot perform actions")
        return replace(self, status=new_status)