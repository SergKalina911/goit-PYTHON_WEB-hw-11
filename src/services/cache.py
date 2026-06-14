""" Модуль для роботи з кешуванням даних користувача у Redis. Цей модуль містить функції для
збереження та отримання даних користувача, таких як email, username, підтвердження реєстрації та
токени доступу. Використання Redis дозволяє швидко отримувати інформацію про користувача без
необхідності звертатися до бази даних при кожному запиті, що покращує продуктивність додатку. """
import os
import redis
import json

# Підключення до Redis
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

def cache_user(user, access_token: str, refresh_token: str) -> None:
    """
    Зберігає дані користувача у Redis.
    Ключ: user:<id>
    Значення: JSON з email, username, confirmed, токенами.
    
    :param user: Об'єкт користувача, який містить інформацію про користувача.
    :type user: repository_users.User
    :param access_token: JWT-токен для доступу.
    :type access_token: str
    :param refresh_token: JWT-токен для оновлення access token.
    :type refresh_token: str
    :return: None
    :rtype: None
    """
    key = f"user:{user.id}"
    redis_client.set(key, json.dumps({
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "confirmed": user.confirmed,
        "access_token": access_token,
        "refresh_token": refresh_token
    }), ex=3600)  # кеш на 1 годину

def get_cached_user(user_id: int) -> dict | None:
    """
    Отримує дані користувача з Redis.
    
    :param user_id: ID користувача для отримання даних.
    :type user_id: int
    :return: Дані користувача або None.
    :rtype: dict or None
    """
    key = f"user:{user_id}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None
