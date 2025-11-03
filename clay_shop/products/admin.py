from django.contrib import admin

from .models import Category, Product, ProductIMG, Review, Service

# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductIMG)
admin.site.register(Service)
admin.site.register(Review)
