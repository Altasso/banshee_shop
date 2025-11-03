from django.contrib import admin

from .models import DeliveryMethod, PaymentMethod

# Register your models here.

admin.site.register(DeliveryMethod)
admin.site.register(PaymentMethod)
