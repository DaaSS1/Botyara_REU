from sqlalchemy import Column, Integer, CHAR, String, TIMESTAMP, TEXT, ForeignKey, DATETIME
from app.core.database import Base

class Solutions(Base):
    __tablename__ = "solutions"
    solution_id = Column(Integer,primary_key=True)
    solver_id = Column(Integer, ForeignKey('tasks.solver_id'))
    answer_text = Column(TEXT)
    is_approved = Column(Integer)
    submitted_at = Column(DATETIME)