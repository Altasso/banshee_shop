from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.http import HttpRequest

from users.models import User
from users.services.user_crud import UserCrud


class AuthService:


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
            content_type=content_type, codename__in=["view_user"]
        )
        seller_group.permissions.set(seller_perms)
        manage_products = Permission.objects.get(
            content_type=content_type, codename="can_manage_products"
        )
        seller_group.permissions.add(manage_products)

        # Admin
        admin_group, _ = Group.objects.ger_or_create(name=User.ADMIN)
        admin_perms = Permission.objects.filter(content_type=content_type)
        admin_group.permissions.set(admin_perms)
