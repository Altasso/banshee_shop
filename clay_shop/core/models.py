from decimal import Decimal

from django.db import models


# Create your models here.
class PaymentMethod(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    processing_fee_percent = models.DecimalField(
        decimal_places=2, max_digits=5, default=Decimal("0.00")
    )
    processing_fee_fixed = models.BigIntegerField(default=0)
    sort_order = models.SmallIntegerField(default=0)

    class Meta:
        verbose_name = "Способ оплаты"
        verbose_name_plural = "Способы оплаты"
        ordering = ["sort_order"]

    def __str__(self):
        return self.name


class DeliveryMethod(models.Model):
    name = models.CharField(max_length=255)
    price = models.BigIntegerField()
    description = models.TextField()
    is_active = models.BooleanField()

    class Meta:
        verbose_name = "Способ доставки"
        verbose_name_plural = "Способы доставки"

    def __str__(self):
        return self.name
