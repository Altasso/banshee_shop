import pytest
from django.core.exceptions import ValidationError

from users.services.user_crud import UserCrud


@pytest.mark.django_db
class TestCrudUserCreate:
    def test_create_user_success(self, user_data):
        user = UserCrud.create_user(user_data)

        assert user is not None
        assert user.id is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.first_name == user_data["first_name"]
        assert user.last_name == user_data["last_name"]
        assert user.role == user_data["role"]
        assert user.check_password(user_data["password"])
        assert user.is_verified is False
        assert user.is_active is True

    def test_create_user_with_verified_flag(self, user_data):
        user_data["is_verified"] = True
        user = UserCrud.create_user(user_data)
        assert user.is_verified is True

    def test_create_user_duplicate_email(self, sample_user, user_data):
        user_data["email"] = sample_user.email

        with pytest.raises(ValidationError) as exc_info:
            UserCrud.create_user(user_data)
        assert "Пользователь с таким email уже существует" in str(exc_info.value)

    def test_create_user_default_role(self, user_data):
        user_data.pop("role")
        user = UserCrud.create_user(user_data)
        assert user.role == "customer"

    def test_create_user_custom_role(self, user_data):
        user_data["role"] = "admin"
        user = UserCrud.create_user(user_data)
        assert user.role == 'admin'
