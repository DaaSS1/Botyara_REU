from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class TaskBase(BaseModel):
    problem_text: str
    subject: str
    status: str
    deadline: datetime | None = None
    images: Optional[List[str]] = None   # ✅ вместо file_id


class TaskCreate(TaskBase):
    user_id: int
    solver_id: Optional[int] = None


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
    answer_text: Optional[str] = None
    file_ids: Optional[List[str]] = None   # список айдишников фото
    caption: Optional[str] = None


class SolutionCreate(BaseModel):
    solver_id: int
    file_ids: List[str]
    caption: Optional[str] = None

class SolutionResponse(SolutionBase):
    solution_id: int
    task_id: int
    is_approved: bool
    submitted_at: datetime

    class Config:
        from_attributes = True