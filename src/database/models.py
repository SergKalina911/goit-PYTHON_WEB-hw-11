""" Модуль для визначення моделей бази даних за допомогою SQLAlchemy. Тут ми створюємо класи User
та Contact, які відповідають таблицям у базі даних. Клас User містить інформацію про користувача,
а клас Contact містить інформацію про контакти, пов'язані з користувачем. Ми також встановлюємо
зв'язок між користувачами та контактами за допомогою зовнішнього ключа. """
from sqlalchemy import Boolean, Column, Integer, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from src.database.db import Base

class User(Base):
    """ 
    Модель користувача, яка відповідає таблиці "users" у базі даних. Вона містить поля для
    зберігання інформації про користувача.
    
    __tablename__ = "users"
    :param id: Унікальний ідентифікатор користувача
    :type id: int
    :param username: Ім'я користувача
    :type username: str
    :param email: Електронна пошта користувача, яка повинна бути унікальною
    :type email: str
    :param password: Хешований пароль користувача
    :type password: str
    :param created_at: Дата та час створення користувача, встановлюється автоматично
    :type created_at: datetime
    :param avatar: URL аватара користувача, може бути null
    :type avatar: str or None
    :param refresh_token: Токен для оновлення сесії користувача, може бути null
    :type refresh_token: str or None
    :param confirmed: Чи підтвердив користувач свою електронну пошту, за замовчуванням False
    :type confirmed: bool
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False) # ✅ email підтвердження


class Contact(Base):
    """ 
    Модель контакту, яка відповідає таблиці "contacts" у базі даних. Вона містить поля для
    зберігання інформації про контакт.
    
    __tablename__ = "contacts"
    :param id: Унікальний ідентифікатор контакту
    :type id: int
    :param first_name: Ім'я контакту
    :type first_name: str
    :param last_name: Прізвище контакту
    :type last_name: str
    :param email: Електронна пошта контакту
    :type email: str
    :param phone: Номер телефону контакту
    :type phone: str
    :param birthday: Дата народження контакту
    :type birthday: date
    :param extra_info: Додаткова інформація про контакт, може бути null
    :type extra_info: str or None
    :param user_id: Ідентифікатор користувача, до якого належить контакт
    :type user_id: int
    :param user: Зв'язок з моделлю User, який дозволяє отримувати інформацію про власника контакту
    :type user: User
    
    """
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String,  index=True, nullable=False)
    phone = Column(String, nullable=False)
    birthday = Column(Date, nullable=False)
    extra_info = Column(String, nullable=True)

    # 🔑 Зв’язок із користувачем
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", backref="contacts")
