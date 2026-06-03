""" Модуль для визначення моделей бази даних за допомогою SQLAlchemy. Тут ми створюємо класи User
та Contact, які відповідають таблицям у базі даних. Клас User містить інформацію про користувача,
а клас Contact містить інформацію про контакти, пов'язані з користувачем. Ми також встановлюємо
зв'язок між користувачами та контактами за допомогою зовнішнього ключа. """
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.database.db import Base

class User(Base):
    """ Модель користувача, яка відповідає таблиці "users" у базі даних. Вона містить поля для
    зберігання інформації про користувача. """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)


class Contact(Base):
    """ Модель контакту, яка відповідає таблиці "contacts" у базі даних. Вона містить поля для
    зберігання інформації про контакт. """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    extra_info = Column(String, nullable=True)

    # 🔑 Зв’язок із користувачем
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="contacts")
