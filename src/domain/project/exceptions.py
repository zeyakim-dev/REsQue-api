class InvalidTitleError(Exception):
    """잘못된 프로젝트 제목 예외"""
    pass

class DuplicateMemberError(Exception):
    """중복 멤버 추가 예외"""
    pass

class InvalidProjectStateError(Exception):
    """잘못된 프로젝트 상태 예외"""
    pass 