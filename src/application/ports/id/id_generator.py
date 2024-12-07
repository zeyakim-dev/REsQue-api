from abc import ABC, abstractmethod
from uuid import UUID

class AbstractIdGenerator(ABC):
    """식별자 생성을 위한 포트입니다.
    
    이 인터페이스는 엔티티의 식별자 생성을 추상화하여,
    애플리케이션이 특정 ID 생성 방식에 의존하지 않도록 합니다.
    """
    
    @abstractmethod
    def generate(self) -> UUID:
        """새로운 식별자를 생성합니다.
        
        Returns:
            UUID: 생성된 고유 식별자
            
        이 메서드는 항상 고유한 식별자를 생성해야 하며,
        생성된 식별자는 시스템 내에서 충돌이 없어야 합니다.
        """
        pass