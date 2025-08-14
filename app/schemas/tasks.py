from pydantic import BaseModel
from datetime import datetime



class TaskBase(BaseModel):
    problem_text: str
    subject: str
    status: str
    deadline: datetime | None = None


class TaskCreate(TaskBase):
    user_id: int
    solver_id: int | None = None


class TaskResponse(TaskBase):
    task_id: int
    user_id: int
    solver_id: int | None = None

    class Config:
        from_attributes = True

class TaskStatusUpdate(BaseModel):
    status: str


# class Task(TaskBase):
#     task_id: int
#     user_id: int
#     status: str
#     created_at: datetime
#     updated_at: Optional[datetime] = None
#
#     class Config:
#         from_attributes = True

class SolutionBase(BaseModel):
    answer_text: str


class SolutionCreate(SolutionBase):
    solver_id: int


class SolutionResponse(SolutionBase):
    solution_id: int
    task_id: int
    is_approved: bool
    submitted_at: datetime

    class Config:
        from_attributes = True