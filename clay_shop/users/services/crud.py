from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from users.models import User


class CrudUser:
    @staticmethod
    def get_all_users() -> QuerySet[User]:
        return User.objects.all().order_by("-created_at")

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:  # type: ignore
            return None

    @staticmethod
    def get_user_by_email(email: str) -> User | None:
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:  # type: ignore
            return None

    @staticmethod
    def create_user(data: dict) -> User:
        if User.objects.filter(email=data.get("email")):
            raise ValidationError("Пользователь с таким email уже существует")
        user = User.objects.create_user(
            username=data.get("username"),
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            password=data.get("password"),
            role=data.get("role"),
            is_verified=data.get("is_verified", False),
        )
        return user

    @staticmethod
    def update_user(user_id: int, data: dict) -> User | None:
        user = CrudUser.get_user_by_id(user_id)
        if not user:
            return None

        email = data.get("email")
        if email and email != user.email:
            if User.objects.filter(email=email).exists():
                raise ValidationError("Пользователь с таким email уже существует")

        for field, value in data.items():
            if field == "password" and value:
                user.set_password(value)

            elif hasattr(user, field) and field not in ["id", "created_at"]:
                setattr(user, field, value)

        user.save()
        return user

    @staticmethod
    def delete_user(user_id: int) -> bool:
        user = CrudUser.get_user_by_id(user_id)
        if user:
            user.delete()
            return True
        return False

    @staticmethod
    def activate_user(user_id: int) -> User | None:
        user = CrudUser.get_user_by_id(user_id)
        if user:
            user.is_active = True
            user.save()
        return user

    @staticmethod
    def deactivate_user(user_id: int) -> User | None:
        user = CrudUser.get_user_by_id(user_id)
        if user:
            user.is_active = False
            user.save()
        return user

    @staticmethod
    def verify_user(user_id: int) -> User | None:
        user = CrudUser.get_user_by_id(user_id)
        if user:
            user.is_verified = True
            user.save()
        return user
