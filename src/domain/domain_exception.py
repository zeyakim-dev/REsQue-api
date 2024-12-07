class DomainException(Exception):
    """도메인 계층의 모든 예외의 기본 클래스입니다."""
    def __init__(self, message: str = None):
        self.message = message
        super().__init__(self.message)