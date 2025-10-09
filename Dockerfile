FROM python:3.12-slim

# рабочая директория
WORKDIR /app

# копируем зависимости
COPY requirements.txt .

# копируем весь проект
COPY app ./app
COPY bot ./bot
COPY config.py .

# устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# добавляем корень проекта в PYTHONPATH, чтобы config.py и app находились в импортах
ENV PYTHONPATH=/app

# запускаем FastAPI и бота одновременно
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 80 & python bot/main.py"]
