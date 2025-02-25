class ItemNotFoundError(Exception):
    """아이템 찾지 못했을때 반환"""
    
    pass

class DuplicateItemFoundError(Exception):
    """중복 아이템 추가시 에러"""

    pass