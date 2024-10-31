from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/users.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread" : False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def initDB():
    """
    데이터베이스 테이블을 초기화합니다.
    SQLAlchemy ORM을 사용하여 모든 모델의 테이블을 생성합니다.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    데이터베이스 세션을 생성하고 반환합니다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

