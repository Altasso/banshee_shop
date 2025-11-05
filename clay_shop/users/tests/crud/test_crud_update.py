import pytest
from django.core.exceptions import ValidationError

from users.services.user_crud import CrudUser


@pytest.mark.django_db
class TestCrudUserUpdate:
    def test_update_user_success(self, sample_user):
        update_data = {
            "first_name": "Updated",
            "last_name": "Name",
            "role": "admin",
        }
        updated_user = CrudUser.update_user(sample_user.id, update_data)
        assert updated_user is not None
        assert updated_user.first_name == "Updated"
        assert updated_user.last_name == "Name"
        assert updated_user.role == "admin"
        assert updated_user.email == sample_user.email

    def test_update_user_not_exists(self):
        updated_user = CrudUser.update_user(999999, {"first_name": "Test"})
        assert updated_user is None

    def test_update_user_email_success(self, sample_user):
        new_email = "newemail@example.com"
        updated_user = CrudUser.update_user(sample_user.id, {"email": new_email})
        assert updated_user is not None
        assert updated_user.email == new_email

    def test_update_user_email_same(self, sample_user):
        update_data = {
            "email": sample_user.email,
            "first_name": "NewName",
        }
        updated_user = CrudUser.update_user(sample_user.id, update_data)

        assert updated_user is not None
        assert updated_user.email == sample_user.email
        assert updated_user.first_name == "NewName"

    def test_update_user_email_duplicate(self, sample_user, create_user):
        another_user = create_user(username="another", email="another@example.com")
        with pytest.raises(ValidationError) as exc_info:
            CrudUser.update_user(sample_user.id, {"email": another_user.email})
        assert "Пользователь с таким email уже существует" in str(exc_info.value)

    def test_update_user_password(self, sample_user):
        new_password = "NewPassword123!"
        updated_user = CrudUser.update_user(sample_user.id, {"password": new_password})

        assert updated_user is not None
        assert updated_user.check_password(new_password)

    def test_update_user_password_empty_string(self, sample_user):
        old_password = "TestPassword123!"
        sample_user.set_password(old_password)
        sample_user.save()

        updated_user = CrudUser.update_user(sample_user.id, {"password": ""})

        assert updated_user is not None
        assert updated_user.check_password(old_password)

    def test_update_user_protected_fields(self, sample_user):
        original_create_at = sample_user.created_at

        update_data = {
            "id": 99999,
            "created_at": "2020-01-01",
            "first_name": "Updated",
        }

        updated_user = CrudUser.update_user(sample_user.id, update_data)
        assert updated_user.id == sample_user.id
        assert updated_user.created_at == original_create_at
        assert updated_user.first_name == 'Updated'

