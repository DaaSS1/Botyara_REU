import logging
from httpx import AsyncClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = "http://localhost:8000"  # Адрес сервера FastAPI

# ---------- TASKS ----------
async def create_task_api(task_data: dict):
        async with AsyncClient(base_url=API_URL) as client:
            resp = await client.post("/create_task", json = task_data)
            resp.raise_for_status()
            return resp.json()

async def get_task_api(task_id: int):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"GET /task/{task_id}")
        resp = await client.get(f"/task/{task_id}")
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def get_tasks_by_user_api(user_id: int):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"GET /tasks_by_user/{user_id}")
        resp = await client.get(f"/tasks_by_user/{user_id}")
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def get_available_tasks_api():
    """Получить все доступные задачи (без назначенного исполнителя)"""
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"GET /available_tasks")
        resp = await client.get("/available_tasks")
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def assign_task_to_solver_api(task_id: int, solver_id: int):
    """Назначить задачу исполнителю"""
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"PATCH /task/{task_id}/assign -> {{'solver_id': {solver_id}}}")
        resp = await client.patch(f"/task/{task_id}/assign", json={"solver_id": solver_id})
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def update_task_status_api(task_id: int, status: str):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"PATCH /{task_id}/status -> {{'status': '{status}'}}")
        resp = await client.patch(f"/{task_id}/status", json={"status": status})
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

# ---------- USERS ----------
async def create_user_api(user_data: dict):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"POST /create_user -> {user_data}")
        resp = await client.post("/create_user", json=user_data)
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def get_user_api(user_id: int):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"GET /user/{user_id}")
        resp = await client.get(f"/user/{user_id}")
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def update_user_api(user_id: int, payload: dict):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"PATCH /user/{user_id} -> {payload}")
        resp = await client.patch(f"/user/{user_id}", json=payload)
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def get_users_api(skip: int = 0, limit: int = 100):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"GET /users?skip={skip}&limit={limit}")
        resp = await client.get(f"/users", params={"skip": skip, "limit": limit})
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

async def get_user_by_username_api(tg_name: str):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info(f"GET /username/{tg_name}")
        resp = await client.get(f"/username/{tg_name}")
        logger.info(f"Response [{resp.status_code}]: {resp.text}")
        resp.raise_for_status()
        return resp.json()

# ---------- SOLUTIONS ----------
async def get_match(task_id: int):
    async with AsyncClient(base_url=API_URL) as client:
        logger.info()