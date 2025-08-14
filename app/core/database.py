# from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker
# from dotenv import load_dotenv
# import os
#
# load_dotenv()
# DATABASE_URL = os.getenv("DB_URL")
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)
#
# Base = declarative_base()
#
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite: асинхронный драйвер — aiosqlite
DATABASE_URL = "sqlite:///./database.db"

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# Dependency — для FastAPI или alembic
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
