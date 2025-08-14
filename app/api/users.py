from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.crud import get_user_by_id, get_users, create_user, get_user_by_tg_name, delete_user
from app.schemas.users import UserCreate, UserResponse
from app.models.users import Users
app = APIRouter()

@app.get("/user/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    # user_id здесь — это Telegram ID пользователя
    db_user = get_user_by_id(db, user_id = user_id)
    if db_user is None:
        raise HTTPException(status_code=400, detail="Пользователь не найден, шлюха")
    return UserResponse.model_validate(db_user)

@app.get("/users")
def get_all_users( db: Session = Depends(get_db)):
    db_users = get_users(db)
    return [UserResponse.model_validate(user) for user in db_users]

@app.get("/username/{tg_name}")
def get_username(tg_name: str, db: Session = Depends(get_db)):
    db_user = get_user_by_tg_name(db, tg_name = tg_name)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(db_user)

@app.post("/create_user")
def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(Users).filter(Users.tg_user_id == user.tg_user_id).first()
    if existing:
        return UserResponse.model_validate(existing)  # Возвращаем схему
    db_user = Users(
        tg_user_id=user.tg_user_id,
        tg_name=user.tg_name,
        role=user.role,
        high_school=user.high_school,
        year=user.year,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserResponse.model_validate(db_user)  # Возвращаем схему

@app.patch("/user/{user_id}")
def update_user(user_id: int, payload: dict, db: Session = Depends(get_db)):
    # user_id здесь — это Telegram ID
    db_user = db.query(Users).filter(Users.tg_user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    allowed_fields = {"tg_name", "role", "high_school", "year"}
    for key, value in payload.items():
        if key in allowed_fields:
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return UserResponse.model_validate(db_user)

@app.delete("/delete_user/{user_id}")
def delete_one_user(user_id: int, db: Session = Depends(get_db)):
    # user_id здесь - это внутренний id пользователя
    deleted = delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}