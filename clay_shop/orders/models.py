from core.models import DeliveryMethod, PaymentMethod
from django.core.validators import MinValueValidator
from django.db import models
from products.models import Product, Service
from users.models import User, UserAddress


# Create your models here.
class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает подтверждения"),
        ("confirmed", "Подтвержден"),
        ("in_production", "В производстве"),
        ("ready", "Готов к отправке"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменен"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Ожидает оплаты"),
        ("paid", "Оплачен"),
        ("refunded", "Возвращен"),
        ("cancelled", "Отменен"),
    ]

    user_id = models.ForeignKey(
        User,
        verbose_name="Кто заказал",
        on_delete=models.PROTECT,
        related_name="orders",
    )
    status = models.CharField(
        verbose_name="Статус заказа", choices=STATUS_CHOICES, default="pending"
    )
    total_amount = models.BigIntegerField(verbose_name="Общая сумма")
    delivery_method_id = models.ForeignKey(
        DeliveryMethod, on_delete=models.PROTECT, related_name="orders"
    )
    delivery_address = models.ForeignKey(
        UserAddress, on_delete=models.PROTECT, related_name="orders"
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.PROTECT, related_name="orders"
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default="pending"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.id} от {self.user_id.email}"


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="order_items"
    )
    quantity = models.SmallIntegerField(validators=[MinValueValidator(1)])
    price = models.BigIntegerField(verbose_name="Цена на момент заказа")
    personalization_text = models.CharField(
        max_length=127, verbose_name="Текст для гравировки", blank=True
    )

    class Meta:
        verbose_name = "Позиция заказа"
        verbose_name_plural = "Позиции заказов"

    def __str__(self):
        return f"{self.product_id.name} x{self.quantity} в заказе №{self.order_id.id}"


class OrderService(models.Model):
    order_item_id = models.ForeignKey(
        OrderItem, on_delete=models.CASCADE, related_name="services"
    )
    service_id = models.ForeignKey(
        Service, on_delete=models.PROTECT, related_name="order_services"
    )
    price = models.BigIntegerField(verbose_name="Цена на момент заказа")
    details = models.CharField(max_length=255, verbose_name="Детали заказа", blank=True)

    class Meta:
        verbose_name = "Услуга в заказе"
        verbose_name_plural = "Услуги в заказах"

    def __str__(self):
        return f"{self.service_id.name} для {self.order_item_id.product.name}"


class OrderStatusHistory(models.Model):
    order_id = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="status_history"
    )
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(blank=True)

    class Meta:
        verbose_name = "История статуса заказа"
        verbose_name_plural = "История статусов заказов"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заказ №{self.order_id.id}: {self.status}"


class Wishlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist")
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="wishlisted_by"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Список желаний"
        verbose_name_plural = "Списки желаний"
        unique_together = ("user_id", "product_id")

    def __str__(self):
        return f"{self.user_id.email} - {self.product_id.name}"


class Cart(models.Model):
    user_id = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="cart_items"
    )
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="in_carts"
    )
    quantity = models.SmallIntegerField(validators=[MinValueValidator(1)])
    personalization_text = models.CharField(max_length=63, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        unique_together = ("user_id", "product_id")

    def __str__(self):
        return f"{self.user_id.email} - {self.product_id.name} x{self.quantity}"

