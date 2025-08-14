from sqlalchemy import Column, Integer,String, BigInteger
from app.core.database import Base

class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    tg_user_id = Column(BigInteger, unique=True, index=True, nullable=False)
    tg_name = Column(String, nullable=True)
    role = Column(String, nullable=False)
    high_school = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
