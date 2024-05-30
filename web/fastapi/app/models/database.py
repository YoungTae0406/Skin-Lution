from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread" : False})
#SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def initDB():
    with engine.connect() as conn:
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            userName TEXT NOT NULL,
            passWordHash TEXT NOT NULL,
            createdAt DATETIME NOT NULL,
            lastLogin DATETIME,
            skinType TEXT
        """))

def get_db():
    db = engine.connect()
    try:
        yield db
    finally:
        db.close()

