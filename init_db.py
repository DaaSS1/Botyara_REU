from app.core.database import engine, Base
from app.models import task, users, payment, solutions, ai_usage  # Импорты нужны!

def init_models():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_models()
