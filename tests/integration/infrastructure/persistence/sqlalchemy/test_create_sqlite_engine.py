from sqlalchemy import text
from sqlalchemy.engine import Engine
from src.infrastructure.persistence.sqlalchemy.config import create_sqlite_engine

class TestSQLiteEngineIntegration:
    """SQLite 인메모리 엔진 생성에 대한 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.config = {
            'url': 'sqlite:///:memory:',
            'connect_args': {
                'check_same_thread': False
            }
        }
        self.engine = create_sqlite_engine(self.config)

    def test_engine_instance_creation(self):
        """엔진 인스턴스 생성 검증"""
        assert isinstance(self.engine, Engine)

    def test_database_connection(self):
        """데이터베이스 연결 검증"""
        with self.engine.begin() as conn:
            version = conn.execute(text("SELECT sqlite_version()")).scalar()
            assert version is not None

    def test_basic_database_operations(self):
        """기본적인 데이터베이스 작업 검증"""
        with self.engine.begin() as conn:
            # 테이블 생성 및 데이터 삽입
            conn.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)"))
            conn.execute(text("INSERT INTO test (id, value) VALUES (1, 'test')"))
            
            # 데이터 조회
            result = conn.execute(text("SELECT * FROM test")).fetchall()
            assert len(result) == 1
            assert result[0][0] == 1
            assert result[0][1] == 'test'

    def test_connection_persistence(self):
        """연결 간 데이터 지속성 검증"""
        # 첫 번째 연결에서 데이터 준비
        with self.engine.begin() as conn:
            conn.execute(text("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)"))
            conn.execute(text("INSERT INTO test (id, value) VALUES (1, 'test')"))

        # 새로운 연결에서 데이터 확인
        with self.engine.begin() as new_conn:
            result = new_conn.execute(text("SELECT * FROM test")).fetchall()
            assert len(result) == 1
            assert result[0][0] == 1
            assert result[0][1] == 'test'