from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
import logging
from users.models import User


logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def assign_role_group(user: User) -> None:
        user.groups.filter(name__in=[User.CUSTOMER, User.SELLER, User.ADMIN]).clear()

        try:
            group = Group.objects.get(name=user.role)  # type: ignore
            user.groups.add(group)
        except Group.DoesNotExist:  # type: ignore
            logger.error(f"Группа {user.role} не найдена для пользователя {user.email}")

    @staticmethod
    def setup_default_groups():
        content_type = ContentType.objects.get_for_model(User)

        # Customer
        customer_group, _ = Group.objects.get_or_create(name=User.CUSTOMER)
        customer_perms = Permission.objects.filter(
            content_type=content_type, codename="view_user"
        )
        customer_group.permissions.set(customer_perms)

        # Seller
        seller_group, _ = Group.objects.get_or_create(name=User.SELLER)
        seller_perms = Permission.objects.filter(
            content_type=content_type, codename__in=["view_user", "can_manage_products"]
        )
        seller_group.permissions.set(seller_perms)

        # Admin
        admin_group, _ = Group.objects.get_or_create(name=User.ADMIN)
        admin_perms = Permission.objects.filter(content_type=content_type)
        admin_group.permissions.set(admin_perms)
