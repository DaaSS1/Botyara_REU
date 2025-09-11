from app.core.database import engine, Base
from app.models import task, users, solutions  # Импорты нужны!

def init_models():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_models()
