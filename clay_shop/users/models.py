from core.models import DeliveryMethod
from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class User(AbstractUser):
    CUSTOMER = "customer"
    SELLER = "seller"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (CUSTOMER, "Покупатель"),
        (SELLER, "Продавец"),
        (ADMIN, "Админ"),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    role = models.CharField(max_length=31, choices=ROLE_CHOICES, default=CUSTOMER)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        permissions = [
            ("can_verify_users", "Может верифицировать пользователей"),
            ("can_manage_products", "Может управлять товарами"),
            ("can_view_all_orders", "Может просматривать все заказы"),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - ({self.email})"

    @property
    def is_customer(self):
        return self.role == self.CUSTOMER

    @property
    def is_seller(self):
        return self.role == self.SELLER

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser


class UserAddress(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="addresses"
    )
    title = models.CharField(max_length=127)
    address = models.TextField()
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Адрес пользователя"
        verbose_name_plural = "Адреса пользователя"

    def __str__(self):
        return f"{self.title}: {self.address}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", primary_key=True
    )
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(null=True, blank=True)
    preferred_delivery_method = models.ForeignKey(
        DeliveryMethod,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="preferred_by_users",
    )

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self):
        return f"Профиль {self.user.email}"
