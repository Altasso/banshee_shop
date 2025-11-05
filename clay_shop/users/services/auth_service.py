from distro import codename
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.http import HttpRequest

from users.models import User


class AuthService:
    @staticmethod
    def login_user(
        request: HttpRequest, email: str, password: str
    ) -> tuple[bool, str, User | None]:
        user = authenticate(request, username=email, password=password)

        if not user:
            return False, "Неверный email или пароль", None

        if not user.is_active:
            return False, "Аккаунт деактивирован", None

        if not user.is_verified:
            return False, "Email не верифицирован", None

        login(request, user)

        return True, "Успешная авторизация", user

    @staticmethod
    def logout(request: HttpRequest) -> None:
        logout(request)

    @staticmethod
    def assign_role_group(user: User) -> None:
        user.groups.filter(name__in=[User.CUSTOMER, User.SELLER, User.ADMIN]).delete()

        try:
            group = Group.object.get(name=user.role)  # type: ignore
            user.groups.add(group)
        except Group.DoesNotExist:  # type: ignore
            pass

    @staticmethod
    def setup_default_groups():
        # Customer
        content_type = ContentType.objects.get_for_model(User)

        customer_group, _ = Group.objects.get_or_create(name=User.CUSTOMER)
        customer_perms = Permission.objects.filter(
            content_type=content_type, codename="view_user"
        )
        customer_group.permissions.set(customer_perms)

        # Seller
        seller_group, _ = Group.objects.get_or_create(name=User.SELLER)
        seller_perms = Permission.objects.filter(
            content_type=content_type,
            codename__in=['view_user']
        )
        seller_group.permissions.set(seller_perms)
        manage_products = Permission.objects.get(
            content_type=content_type,
            codename='can_manage_products'
        )
        seller_group.permissions.add(manage_products)

        # Admin
        admin_group, _ = Group.objects.ger_or_create(name=User.ADMIN)
        admin_perms = Permission.objects.filter(content_type=content_type)
        admin_group.permissions.set(admin_perms)
