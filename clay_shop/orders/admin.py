from django.contrib import admin

from .models import Cart, Order, OrderItem, OrderService, OrderStatusHistory, Wishlist

# Register your models here.

admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(OrderService)
admin.site.register(OrderStatusHistory)
admin.site.register(Wishlist)
admin.site.register(Cart)
