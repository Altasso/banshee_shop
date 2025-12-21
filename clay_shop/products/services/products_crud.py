from typing import Any, Dict, List

from django.db import transaction
from django.db.models import Avg, Count, Q, QuerySet

from products.models import Product, ProductIMG


class ProductsService:
    @staticmethod
    def get_active_products() -> QuerySet:
        return Product.objects.filter(is_active=True).select_related("category_id")

    @staticmethod
    def get_all_products() -> QuerySet:
        return Product.objects.select_related("category_id").prefetch_related("images")

    @staticmethod
    def get_product_by_id(product_id: int) -> Product | None:
        try:
            return (
                Product.objects.select_related("category_id")
                .prefetch_related("images")
                .get(id=product_id, is_active=True)
            )
        except Product.DoesNotExist:
            return None

    @staticmethod
    def get_product_by_id_for_seller(product_id: int) -> Product | None:
        try:
            return (
                Product.objects.select_related("category_id")
                .prefetch_related("images")
                .get(id=product_id)
            )
        except Product.DoesNotExist:
            return None

    @staticmethod
    def get_products_by_category(category_id: int) -> QuerySet:
        return (
            Product.objects.filter(category_id=category_id, is_active=True)
            .select_related("category_id")
            .prefetch_related("images")
        )

    @staticmethod
    def search_products(query: str) -> QuerySet:
        return Product.objects.filter(
            Q(name__icontains=query) | Q(desription__icointains=query), is_active=True
        ).select_related("category_id")

    @staticmethod
    def filter_products_for_seller(
        status: str | None = None,
        search: str | None = None,
        sort_by: str = "-created_at",
    ) -> QuerySet:
        queryset = ProductsService.get_all_products()

        if status == "active":
            queryset = queryset.filter(is_active=True)
        elif status == "inactive":
            queryset = queryset.filter(is_active=False)
        elif status == "out_of_stock":
            queryset = queryset.filter(stock_quantity=0)

        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description_icontains=search)
            )
        queryset = queryset.order_by(sort_by)

        return queryset

    @staticmethod
    @transaction.atomic
    def create_product(
        product_data: dict[str, Any], images: list[dict[str, Any]]
    ) -> Product:
        product = Product.objects.create(**product_data)

        for img_data in images:
            ProductIMG.objects.create(product_id=product, **img_data)

        return product

    @staticmethod
    @transaction.atomic
    def update_product(product_id: int, product_data: dict[str, Any]) -> Product | None:
        try:
            product = Product.objects.get(id=product_id)
            for key, value in product_data.items():
                setattr(product, key, value)
            product.save()
            return product
        except Product.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def toggle_product_active(product_id: int) -> bool | None:
        try:
            product = Product.objects.get(id=product_id)
            product.is_active = not product.is_active
            product.save()
            return product.is_active
        except Product.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def update_stock(product_id: int, action: str, quantity: int) -> int | None:
        try:
            product = Product.objects.select_for_update().get(id=product_id)

            if action == "add":
                product.stock_quantity += quantity
            elif action == "set":
                product.stock_quantity = quantity
            elif action == "substract":
                product.stock_quantity = max(0, product.stock_quantity - quantity)

            product.save()
            return product.stock_quantity
        except Product.DoesNotExist:
            return None

    @staticmethod
    def check_availability(product_id: int, quantity: int = 1) -> bool:
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            if product.is_unique:
                return product.stock_quantity > 0
            return product.stock_quantity >= quantity
        except Product.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def decrease_stock(product_id: int, quantity: int = 1) -> bool:
        try:
            product = Product.objects.select_for_update().get(id=product_id)
            if product.stock_quantity >= quantity:
                product.stock_quantity -= quantity
                product.save()
                return True
            return False
        except Product.DoesNotExist:
            return False

    @staticmethod
    def get_product_with_reviews(product_id: int) -> dict[str, Any] | None:
        try:
            product = Product.objects.annotate(
                avg_rating=Avg("review__rating"), review_count=Count("review")
            ).get(id=product_id, is_active=True)

            return {
                "product": product,
                "avg_rating": product.avg_rating or 0,
                "review_count": product.review_count,
            }
        except Product.DoesNotExist:
            return None

    @staticmethod
    def get_low_stock_products(threshold: int = 5) -> QuerySet:
        return Product.objects.filter(
            stock_quantity__lte=threshold, stock_quantity__gt=0
        ).order_by("stock_quantity")

    @staticmethod
    def get_out_of_stock_count() -> int:
        return Product.objects.filter(stock_quantity=0).count()

    @staticmethod
    def get_popular_products(limit: int = 5) -> QuerySet:
        return Product.objects.annotate(review_count=Count('review')).order_by('-review_count')[:limit]
