from sqlalchemy import Column, Integer, TEXT, FLOAT, ForeignKey
from app.core.database import Base

class AIUsage(Base):
    __tablename__ = "ai_usage"
    request_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    promt_ai = Column(TEXT)
    response = Column(TEXT)
    tokens_used = Column(Integer)
    promt_cost = Column(FLOAT)
