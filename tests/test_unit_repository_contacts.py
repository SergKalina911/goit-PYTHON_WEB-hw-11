""" Юнит-тесты для репозитория контактов. """

import unittest
from unittest.mock import MagicMock
from src.database.models import User, Contact
from src.schemas import ContactCreate, ContactUpdate
from src.repository import contacts as repository_contacts


class TestContactsRepository(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock()
        self.user = User(id=1, email="test@example.com")

    async def test_create_contact(self):
        contact_data = ContactCreate(
            first_name="Ivan",
            last_name="Petrenko",
            email="ivan@example.com",
            phone="123456789",
            birthday="2000-01-01",
            extra_info="Friend"
        )
        contact = await repository_contacts.create_contact(self.session, contact_data, self.user)
        self.assertIsInstance(contact, Contact)
        self.assertEqual(contact.email, "ivan@example.com")

    async def test_get_contacts(self):
        self.session.query().filter().all.return_value = []
        contacts = await repository_contacts.get_contacts(self.session, self.user)
        self.assertIsInstance(contacts, list)

    async def test_get_contact(self):
        contact = Contact(id=1, email="ivan@example.com")
        self.session.query().filter().first.return_value = contact
        result = await repository_contacts.get_contact(self.session, 1, self.user)
        self.assertEqual(result.email, "ivan@example.com")

    async def test_update_contact(self):
        contact = Contact(id=1, email="ivan@example.com", phone="123456789")
        self.session.query().filter().first.return_value = contact
        updated = await repository_contacts.update_contact(
            self.session, 1,
            ContactUpdate(
                first_name="Ivan",
                last_name="Petrenko",
                email="ivan@example.com",
                phone="987654321",
                birthday="2000-01-01",
                extra_info="Friend"
            ),
            self.user
        )
        self.assertEqual(updated.phone, "987654321")

    async def test_delete_contact(self):
        contact = Contact(id=1, email="ivan@example.com")
        self.session.query().filter().first.return_value = contact
        deleted = await repository_contacts.delete_contact(self.session, 1, self.user)
        self.assertIsInstance(deleted, Contact)

    async def test_search_contacts(self):
        self.session.query().filter().all.return_value = []
        results = await repository_contacts.search_contacts(self.session, "Ivan", self.user)
        self.assertIsInstance(results, list)

    async def test_upcoming_birthdays(self):
        self.session.query().filter().all.return_value = []
        results = await repository_contacts.upcoming_birthdays(self.session, self.user)
        self.assertIsInstance(results, list)


if __name__ == "__main__":
    unittest.main()
