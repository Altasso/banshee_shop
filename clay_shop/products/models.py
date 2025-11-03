from django.db import models
from users.models import UserProfile


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField()

    class Meta:
        ordering = ["name"]
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=127, verbose_name="Название")
    description = models.CharField(max_length=127, verbose_name="Описание")
    base_price = models.IntegerField(verbose_name="Базовая цена")
    discount_price = models.IntegerField(verbose_name="Цена со скидкой")
    is_unique = models.BooleanField(verbose_name="Уникальное ли", default=True)
    stock_quantity = models.IntegerField(verbose_name="Количество на складе", default=0)
    category_id = models.ForeignKey(
        Category, on_delete=models.PROTECT, related_name="products"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    manufacturing_time_days = models.IntegerField(verbose_name="Время изготовления")
    materials = models.CharField(max_length=255, verbose_name="Материалы изделия")
    weight = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Вес")
    size = models.DecimalField(max_digits=7, decimal_places=2, verbose_name="Размер")

    class Meta:
        ordering = ["name"]
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.name


class ProductIMG(models.Model):
    product_id = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image_url = models.URLField()
    is_main = models.BooleanField(default=True, verbose_name="Главное ли фото")
    order = models.SmallIntegerField(default=0, verbose_name="Порядок показа")

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ["order"]
        unique_together = ('product_id', 'order')

    def __str__(self):
        return f"Изображения для {self.product_id.name}"


class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(verbose_name="Описание услуги")
    price = models.BigIntegerField(verbose_name="Дополнительная стоимость")
    is_active = models.BooleanField(verbose_name="Возможно ли", default=True)

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.name


class Review(models.Model):
    RATING_CHOICES = [
        (1, "1 звезда"),
        (2, "2 звезды"),
        (3, "3 звезды"),
        (4, "4 звезды"),
        (5, "5 звезд"),
    ]

    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    rating = models.SmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField()

    class Meta:
        verbose_name = "Продукт"
        verbose_name_plural = "Продукты"

    def __str__(self):
        return self.product_id
