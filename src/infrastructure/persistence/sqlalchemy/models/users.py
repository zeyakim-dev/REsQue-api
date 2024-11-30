from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from src.infrastructure.persistence.sqlalchemy.models.base import Base
from sqlalchemy import String

class UserModel(Base):
    __tablename__ = 'users'
    
    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(50), 
        unique=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255)
    )
    
    def __repr__(self) -> str:
        return f"User(id={self.id}, username={self.username})"