import pytest
from typing import Dict, Type, Callable
from uuid import UUID as PyUUID, uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.infrastructure.persistence.sqlalchemy.models.base import Base
from src.infrastructure.persistence.sqlalchemy.repositories.base_repository import SQLAlchemyRepository
from src.domain.entity import Entity
from src.infrastructure.persistence.sqlalchemy.uow import SQLAlchemyUnitOfWork
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

# 테스트용 모델과 엔티티
class TestEntity(Entity):
    def __init__(self, id: PyUUID, value: str):
        super().__init__(id)
        self.value = value

class TestModel(Base):
    __tablename__ = "testmodels"

    id: Mapped[PyUUID] = mapped_column(UUID(as_uuid=True), primary_key=True)
    value: Mapped[int] = mapped_column()

class TestRepository(SQLAlchemyRepository[TestModel, TestEntity]):
    def _to_model(self, entity: TestEntity) -> TestModel:
        return TestModel(id=entity.id, value=entity.value)
        
    def _to_domain(self, model: TestModel) -> TestEntity:
        return TestEntity(id=model.id, value=model.value)

class TestSQLAlchemyUnitOfWorkIntegration:
    """SQLAlchemy UnitOfWork 통합 테스트"""

    @pytest.fixture(scope="function")
    def engine(self):
        """테스트용 SQLite 엔진 생성"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        yield engine
        Base.metadata.drop_all(engine)

    @pytest.fixture(scope="function")
    def session_factory(self, engine):
        """테스트용 세션 팩토리 생성"""
        return sessionmaker(bind=engine)

    @pytest.fixture(scope="function")
    def repositories(self) -> Dict[Type[SQLAlchemyRepository], Callable[[Session], SQLAlchemyRepository]]:
        """테스트용 레포지토리 팩토리 딕셔너리"""
        return {
            TestRepository: lambda session: TestRepository(session, TestModel)
        }

    @pytest.fixture(scope="function")
    def uow(self, session_factory, repositories):
        """테스트용 UnitOfWork 생성"""
        return SQLAlchemyUnitOfWork(session_factory, repositories)

    def test_uow_lifecycle(self, uow):
        """UnitOfWork 생명주기 테스트"""
        # UoW 시작 전
        assert uow._session is None

        with uow:
            # UoW 시작 후
            assert uow._session is not None
            assert uow._session.is_active

        # UoW 종료 후
        assert uow._session is None

    def test_uow_double_entry_prevention(self, uow):
        """UnitOfWork 중첩 진입 방지 테스트"""
        with uow:
            with pytest.raises(RuntimeError, match="이미 활성화된 UnitOfWork가 존재합니다"):
                with uow:
                    pass

    def test_uow_repository_management(self, uow):
        """UnitOfWork의 레포지토리 관리 테스트"""
        with uow:
            # 지원하는 레포지토리 타입
            repo = uow.get_repository(TestRepository)
            assert isinstance(repo, TestRepository)
            
            # 동일한 타입 요청 시 같은 인스턴스 반환
            repo2 = uow.get_repository(TestRepository)
            assert repo is repo2
            
            # 지원하지 않는 레포지토리 타입
            class UnsupportedRepo(SQLAlchemyRepository):
                pass
                
            with pytest.raises(KeyError, match="지원하지 않는 레포지토리 타입입니다"):
                uow.get_repository(UnsupportedRepo)

    def test_uow_transaction_commit(self, uow):
        """UnitOfWork 트랜잭션 커밋 테스트"""
        test_id = uuid4()
        test_value = 42

        # 데이터 생성
        with uow:
            repo = uow.get_repository(TestRepository)
            entity = TestEntity(id=test_id, value=test_value)
            repo.add(entity)
            
        # 새로운 UoW에서 데이터 확인
        with uow:
            repo = uow.get_repository(TestRepository)
            saved_entity = repo.get(test_id)
            assert saved_entity is not None
            assert saved_entity.id == test_id
            assert saved_entity.value == test_value

    def test_uow_transaction_rollback(self, uow):
        """UnitOfWork 트랜잭션 롤백 테스트"""
        test_id = uuid4()
        test_value = 42

        # 먼저 성공하는 트랜잭션으로 테스트 준비
        with uow:
            repo = uow.get_repository(TestRepository)
            entity = TestEntity(id=test_id, value=test_value)
            repo.add(entity)
            
        # 실패하는 트랜잭션 시도
        try:
            with uow:
                repo = uow.get_repository(TestRepository)
                new_entity = TestEntity(id=uuid4(), value=100)
                repo.add(new_entity)
                raise ValueError("의도적인 에러 발생")
        except ValueError:
            pass
            
        # 롤백 확인
        with uow:
            repo = uow.get_repository(TestRepository)
            # 첫 번째 엔티티는 여전히 존재
            assert repo.get(test_id) is not None
            # 실패한 트랜잭션의 엔티티는 저장되지 않음
            result = uow._session.query(TestModel).count()
            assert result == 1