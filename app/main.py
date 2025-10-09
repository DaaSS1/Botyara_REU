from fastapi import FastAPI
from app.api import users, tasks, solutions

app = FastAPI()

app.include_router(users.app)
app.include_router(tasks.router)
app.include_router(solutions.router)