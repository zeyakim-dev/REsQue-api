class HandlerNotFoundError(Exception):
    """등록된 핸들러가 없을 때 발생하는 예외"""
    def __init__(self, message_type):
        super().__init__(f"등록된 핸들러가 없습니다. 메시지 타입: {message_type}")

class DuplicateHandlerError(Exception):
    """핸들러가 중복 등록될 때 발생하는 예외"""
    def __init__(self, message_type):
        super().__init__(f"핸들러가 이미 등록되었습니다. 메시지 타입: {message_type}") 