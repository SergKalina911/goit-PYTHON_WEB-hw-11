.PHONY: up down run tests coverage testfile logs migrate revision

# Запустити всі сервіси у Docker (продакшн/розробка)
up:
    docker-compose up -d --build

# Зупинити всі сервіси
down:
    docker-compose down

# Запустити тільки застосунок (web + залежності) без тестів
run:
    docker-compose up -d web

# Запустити всі тести всередині контейнера web (без покриття)
tests:
    docker-compose -f docker-compose.yml -f docker-compose.override.yml exec web poetry run pytest -v

# Запустити всі тести з покриттям коду
coverage:
    docker-compose -f docker-compose.yml -f docker-compose.override.yml exec web poetry run pytest --cov=src --cov-report=term-missing -v

# Запустити конкретний тестовий файл: make testfile file=tests/test_unit_services_auth.py
testfile:
    docker-compose -f docker-compose.yml -f docker-compose.override.yml exec web poetry run pytest $(file) -v

# Переглянути логи контейнера web
logs:
    docker-compose logs -f web

# Виконати міграції бази даних
migrate:
    docker-compose exec web alembic upgrade head

# Створити нову ревізію міграції: make revision msg="add new table"
revision:
    docker-compose exec web alembic revision --autogenerate -m "$(msg)"
