class InvalidTitleError(Exception):
    """잘못된 프로젝트 제목 예외"""
    pass

class DuplicateMemberError(Exception):
    """중복 멤버 추가 예외"""
    pass

class DuplicateInvitationError(Exception):
    """중복 초대 시도 예외"""
    pass

class InvalidRoleError(Exception):
    """잘못된 역할 지정 예외"""
    pass

class InvalidProjectStateError(Exception):
    """잘못된 프로젝트 상태 예외"""
    pass 

