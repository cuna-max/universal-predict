"""SQLite 데이터베이스 관리."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class Database:
    """SQLite 데이터베이스 관리자."""

    def __init__(self, db_path: Path) -> None:
        """초기화."""
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

        # 테이블 생성
        Base.metadata.create_all(self.engine)

    def get_session(self):
        """세션 생성."""
        return self.SessionLocal()

