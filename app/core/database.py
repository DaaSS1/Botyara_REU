from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL


# Вызов переменных из окружения (рекомендуется)
DATABASE_URL = DATABASE_URL

# Синхронный engine (как у тебя было для sqlite, но теперь для Postgres)
engine = create_engine(DATABASE_URL, echo=True)

# Синхронный sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency — для FastAPI или других мест
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
