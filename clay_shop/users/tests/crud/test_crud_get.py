import pytest

from users.services.crud import CrudUser


@pytest.mark.django_db
class TestCrudUserGet:
    def test_get_all_users_empty(self):
        users = CrudUser.get_all_users()
        assert users.count() == 0

    def test_get_all_users(self, multiple_user):
        users = CrudUser.get_all_users()
        assert users.count() == 5
        assert list(users) == sorted(users, key=lambda u: u.created_at, reverse=True)

    def test_get_user_by_id_exists(self, sample_user):
        user = CrudUser.get_user_by_id(sample_user.id)
        assert user is not None
        assert user.id == sample_user.id
        assert user.email == sample_user.email

    def test_get_user_by_id_not_exists(self):
        user = CrudUser.get_user_by_id(99999999)
        assert user is None

    def test_get_user_by_email_exists(self, sample_user):
        user = CrudUser.get_user_by_email(sample_user.email)
        assert user is not None
        assert user.email == sample_user.email
        assert user.id == sample_user.id

    def test_get_user_by_email_not_exists(self):
        user = CrudUser.get_user_by_email("nonexistent@example.com")
        assert user is None
