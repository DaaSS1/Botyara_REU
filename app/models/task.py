from sqlalchemy import Column,Integer,CHAR, String, TIMESTAMP, TEXT, JSON
from app.core.database import Base

class Tasks(Base):
    __tablename__ = "tasks"
    task_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)  # Будем хранить tg_user_id напрямую
    problem_text = Column(TEXT)
    subject = Column(String)
    solver_id = Column(Integer, nullable=True)
    status = Column(String)
    deadline = Column(TIMESTAMP)
    images = Column(JSON, nullable=True )