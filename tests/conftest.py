""" Конфігураційний файл для pytest, який забезпечує налаштування та фікстури для тестів. """

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from src.database.db import SessionLocal
from src.database import models

# Для юніт‑тестів (автоматично очищає перед кожним тестом)
@pytest.fixture(autouse=True)
def clean_db():
    db = SessionLocal()
    try:
        db.query(models.Contact).delete()
        db.query(models.User).delete()
        db.commit()
    finally:
        db.close()

# Для функціональних тестів (очищає лише один раз на початку тесту)
@pytest.fixture
def reset_db():
    db = SessionLocal()
    db.query(models.Contact).delete()
    db.query(models.User).delete()
    db.commit()
    db.close()
