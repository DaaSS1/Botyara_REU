from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.tasks import TaskCreate, TaskStatusUpdate, TaskResponse
from app.core.crud import get_task, get_active_task, create_task, update_task_status, get_tasks_by_user, get_tasks, \
    get_available_tasks_crud, assign_task_to_solver_crud, delete_task
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    return get_tasks(db)

@router.get("/task/{task_id}", response_model=TaskResponse)
def get_one_task(task_id: int, db: Session = Depends(get_db)):
    db_task = get_task(db, task_id)
    return db_task

@router.get("/active_tasks")
def active_tasks(deadline: datetime, db: Session = Depends(get_db)):
    return get_active_task(db, deadline)

@router.post("/new_task")
def new_task(task_in: TaskCreate, db: Session = Depends(get_db)):
    logger.info(f"Получен запрос на создание задачи: {task_in}")
    result = create_task(db, task_in, task_in.user_id)
    logger.info(f"Задача создана: {result}")
    return result


@router.get("/tasks_by_user/{user_id}")
def get_user_tasks(user_id: int, db: Session = Depends(get_db)):
    # user_id здесь - это tg_user_id
    tasks = get_tasks_by_user(db, user_id)
    if not tasks:
        raise HTTPException(status_code=404, detail = "Tasks not found")
    return tasks

@router.get("/available_tasks")
def get_available_tasks(db: Session = Depends(get_db)):
    """Получить все доступные задачи (без назначенного исполнителя)"""
    tasks = get_available_tasks_crud(db)
    return tasks

@router.patch("/task/{task_id}/assign")
def assign_task_to_solver(task_id: int, solver_data: dict, db: Session = Depends(get_db)):
    """Назначить задачу исполнителю"""
    solver_id = solver_data.get("solver_id")
    if not solver_id:
        raise HTTPException(status_code=400, detail="solver_id is required")
    
    result = assign_task_to_solver_crud(db, task_id, solver_id)
    if not result:
        raise HTTPException(status_code=404, detail="Task not found or already assigned")
    return result

@router.delete("/delete_task/{task_id}")
def delete_one_task(task_id:int, db: Session = Depends(get_db)):
    deleted = delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}