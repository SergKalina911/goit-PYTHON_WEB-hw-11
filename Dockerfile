FROM python:3.13-slim

WORKDIR /app

# Встановлюємо Poetry
RUN pip install --upgrade pip && pip install poetry

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-root

COPY ./src ./src
COPY ./main.py ./main.py
COPY alembic.ini .
COPY alembic alembic

# Копіюємо тести
COPY ./tests ./tests

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
