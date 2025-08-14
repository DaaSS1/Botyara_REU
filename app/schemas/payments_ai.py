from pydantic import BaseModel
from typing import Optional


class PaymentBase(BaseModel):
    amount: float
    status_payment: str
    external_id: str


class PaymentCreate(PaymentBase):
    user_id: int
    task_id: int


class PaymentResponse(PaymentBase):
    payment_id: int

    class Config:
        from_attributes = True


class AIUsageBase(BaseModel):
    promt_ai: str
    tokens_used: int
    promt_cost: float


class AIUsageCreate(AIUsageBase):
    user_id: int
    task_id: int


class AIUsageResponse(AIUsageBase):
    request_id: int
    response: str | None = None

    class Config:
        from_attributes = True