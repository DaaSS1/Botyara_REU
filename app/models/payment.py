from sqlalchemy import Column, Integer, String, ForeignKey
from app.core.database import Base

class Payments(Base):
    __tablename__ = "payments"
    payment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Integer)
    status_payment = Column(String)
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    external_id = Column(Integer) #id платежа в платежной системе