""" Юніт-тести для репозиторію користувачів. """

import unittest
from unittest.mock import MagicMock
from src.database.models import User
from src.schemas import UserModel
from src.repository import users as repository_users


class TestUsersRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock()
        self.user_data = UserModel(
            username="testuser",
            email="test@example.com",
            password="hashed_password"
        )
        self.user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password="hashed_password",
            confirmed=False
        )

    async def test_create_user(self):
        user = await repository_users.create_user(self.user_data, self.session)
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test@example.com")

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        user = await repository_users.get_user_by_email("ghost@example.com", self.session)
        self.assertIsNone(user)

    async def test_update_token(self):
        await repository_users.update_token(self.user, "new_token", self.session)
        self.assertEqual(self.user.refresh_token, "new_token")

    async def test_confirmed_email(self):
        # імітуємо, що користувач існує
        self.session.query().filter().first.return_value = self.user
        await repository_users.confirmed_email("test@example.com", self.session)
        self.assertTrue(self.user.confirmed)


if __name__ == "__main__":
    unittest.main()
