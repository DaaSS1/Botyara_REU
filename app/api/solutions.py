from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from datetime import datetime
import logging

from app.models.solutions import Solutions
from app.models.task import Tasks
from app.schemas.tasks import SolutionCreate

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/tasks/{task_id}/solutions")
def create_solution(task_id: int, solution: SolutionCreate, db: Session = Depends(get_db)):
    task = db.query(Tasks).filter(Tasks.task_id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail= "Task not found")

    sol = Solutions(
        task_id = task_id,
        solver_id = solution.solver_id,
        file_ids = solution.file_ids,
        caption = solution.caption,
        submitted_at = datetime.utcnow()
    )
    db.add(sol)
    db.commit()
    db.refresh(sol)

    return {"solution": sol, "task_user_id": task.user_id }