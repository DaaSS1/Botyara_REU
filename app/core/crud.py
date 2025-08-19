from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.task import Tasks
from app.models.users import Users
from app.models.payment import Payments
from app.models.ai_usage import AIUsage
from app.models.solutions import Solutions
from app.schemas.tasks import TaskCreate, TaskResponse
from app.schemas.users import UserCreate
from app.schemas.payments_ai import PaymentResponse

# ========== Users CRUD ==========
def create_user(db: Session, user: UserCreate) -> Users:
    db_user = Users(
        tg_user_id=user.tg_user_id,
        tg_name=user.tg_name,
        role=user.role,
        high_school=user.high_school,
        year=user.year
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> Optional[Users]:
    # Здесь user_id понимаем как Telegram ID пользователя
    return db.query(Users).filter(Users.tg_user_id == user_id).first()

def get_user_by_tg_name(db: Session, tg_name: str) -> Optional[Users]:
    return db.query(Users).filter(Users.tg_name == tg_name).first()

def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[Users]:
    return db.query(Users).offset(skip).limit(limit).all()

# def update_user_role(db: Session, user_id: int, new_role: str) -> Optional[Users]:
#     db_user = db.query(Users).filter(Users.id == user_id).first()
#     if db_user:
#         db_user.role = new_role
#         db.commit()
#         db.refresh(db_user)
#     return db_user

def delete_user(db: Session, user_id: int) -> bool:
    # user_id здесь - это внутренний id пользователя
    db_user = db.query(Users).filter(Users.id == user_id).first()
    if not db_user:
        return False

    db.delete(db_user)
    db.commit()
    return True

# ========== Tasks CRUD ==========

def get_tasks(db: Session, skip: int = 0, limit: int = 100) -> List[Tasks]:
    return db.query(Tasks).offset(skip).limit(limit).all()

def get_task(db: Session, task_id: int):
    task = db.query(Tasks).filter(Tasks.task_id == task_id).first()
    return TaskResponse.model_validate(task) if task else None

def get_active_task(db: Session, deadline: datetime):
    tasks = db.query(Tasks)\
    .filter(Tasks.deadline > deadline)\
    .filter(Tasks.status == 'active').all()
    return [TaskResponse.model_validate(t) for t in tasks]

def create_task(db: Session, task: TaskCreate):
    db_task = Tasks(
        user_id=task.user_id,
        problem_text=task.problem_text,
        subject=task.subject,
        solver_id=task.solver_id,
        status=task.status,
        deadline=task.deadline,
        images=task.images,  # <— добавили
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db: Session, task_id: int):
    db_task = db.query(Tasks).filter(Tasks.task_id == task_id).first()
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True

def update_task_status(db: Session, task_id: int, status: str):
    db_task = db.query(Tasks).filter(Tasks.task_id == task_id).first()
    if not db_task:
        return None
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task

def get_tasks_by_user(db: Session, user_id: int):
    # user_id здесь - это tg_user_id
    tasks = db.query(Tasks).filter(Tasks.user_id == user_id).all()
    return [TaskResponse.model_validate(t) for t in tasks]

def get_available_tasks_crud(db: Session):
    """Получить все доступные задачи (без назначенного исполнителя)"""
    tasks = db.query(Tasks).filter(Tasks.solver_id.is_(None)).filter(Tasks.status == "waiting_for_solver").all()
    return [TaskResponse.model_validate(t) for t in tasks]

def assign_task_to_solver_crud(db: Session, task_id: int, solver_id: int):
    """Назначить задачу исполнителю"""
    task = db.query(Tasks).filter(Tasks.task_id == task_id).first()
    if not task or task.solver_id is not None:
        return None

    task.solver_id = solver_id
    task.status = "assigned"
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)

# ========== Payments CRUD ==========
def get_payments_by_task(db: Session, task_id: int) -> List[Payments]:
    payments = db.query(Payments).filter(Payments.task_id == task_id).all()
    return payments

def get_payments_by_status(db: Session, status: str) -> List[Payments]:
    return db.query(Payments).filter(Payments.status_payment == status).all()

# ========== Solutions CRUD ==========
def get_approved_solutions(db: Session, task_id: int) -> List[Solutions]:
    return db.query(Solutions).filter(Solutions.task_id == task_id).filter(Solutions.is_approved == True).all()

# ========== TaskSolverMatch CRUD ==========
#def get_match(db: Session, match_id: int) -> Optional[TaskSolverMatch]:
 #   return db.query(TaskSolverMatch).filter(TaskSolverMatch.match_id == match_id).first()

# ========== AIUsage CRUD ==========
def get_ai_usage_stats(db: Session, user_id: int) -> dict:
    usages = db.query(AIUsage).filter(AIUsage.user_id == user_id).all()
    return {
        "total_requests": len(usages),
        "total_tokens": sum(u.tokens_used for u in usages),
        "total_cost": sum(u.promt_cost for u in usages)
    }