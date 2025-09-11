from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

_admins_raw = os.getenv("ADMIN_IDS", "")  # например: "13141,313412"
if _admins_raw:
    try:
        ADMIN_IDS = [int(x.strip()) for x in _admins_raw.split(",") if x.strip()]
    except ValueError:
        # на случай, если кто-то случайно положил нечисловые значения
        ADMIN_IDS = []
else:
    ADMIN_IDS = []

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{POSTGRES_DB}"

PersonalAcc = os.getenv("PersonalAcc")
CorrespAcc = os.getenv("CorrespAcc")
PayeeINN = os.getenv("PayeeINN")