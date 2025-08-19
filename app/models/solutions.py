from sqlalchemy import Column, Integer, CHAR, String, TIMESTAMP, TEXT, ForeignKey, DATETIME, JSON
from app.core.database import Base

class Solutions(Base):
    __tablename__ = "solutions"
    solution_id = Column(Integer,primary_key=True)
    solver_id = Column(Integer, ForeignKey('tasks.solver_id'))
    task_id = Column(Integer, ForeignKey("tasks.task_id"))
    file_ids = Column(JSON, nullable=True)  # Telegram file_id (строка)
    caption = Column(String, nullable=True)  # подпись/текст решения (опц.
    is_approved = Column(Integer)
    submitted_at = Column(DATETIME)