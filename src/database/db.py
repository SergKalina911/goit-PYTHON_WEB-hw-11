""" Модуль для налаштування бази даних за допомогою SQLAlchemy. Тут ми створюємо двигун бази даних,
сесію та базовий клас для моделей. Також визначаємо функцію get_db для отримання сесії бази даних у
маршрутах.  """
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mysecretpassword")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "contacts_db")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> SessionLocal:
    """
    Функція для отримання сесії бази даних. Використовується як залежність у маршрутах для
    забезпечення доступу до бази даних.
    
    :return: Сесія бази даних
    :rtype: SessionLocal
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
